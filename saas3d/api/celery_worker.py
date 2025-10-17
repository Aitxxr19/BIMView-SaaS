"""
Worker de Celery para procesamiento asíncrono de nubes de puntos
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun
import os
import logging
from pathlib import Path
from typing import Dict, Any
import traceback

from processing.point_cloud_processor_simple import PointCloudProcessor
from database import SessionLocal
from models import Job
from enums import JobStatus

# Configuración de Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6380/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6380/1")

celery_app = Celery(
    "saas3d_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos máximo
    task_soft_time_limit=25 * 60,  # 25 minutos soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='process_point_cloud')
def process_point_cloud_task(self, job_id: int, input_file_path: str, 
                           algorithm: str = 'poisson', **kwargs) -> Dict[str, Any]:
    """
    Tarea principal para procesar nube de puntos
    
    Args:
        job_id: ID del trabajo en la base de datos
        input_file_path: Ruta al archivo de entrada
        algorithm: Algoritmo de reconstrucción ('poisson', 'ball_pivoting', 'alpha_shape')
        **kwargs: Parámetros adicionales del algoritmo
    
    Returns:
        Dict con el resultado del procesamiento
    """
    db = SessionLocal()
    processor = PointCloudProcessor()
    
    try:
        # Actualizar estado del trabajo
        update_job_status(db, job_id, JobStatus.processing, progress=5)
        
        # Cargar nube de puntos
        logger.info(f"Iniciando procesamiento para job {job_id}")
        if not processor.load_point_cloud(input_file_path):
            raise Exception("Error al cargar la nube de puntos")
        
        update_job_status(db, job_id, JobStatus.processing, progress=15)
        
        # Preprocesamiento
        logger.info("Aplicando preprocesamiento...")
        
        # Downsampling
        voxel_size = kwargs.get('voxel_size', 0.01)
        if not processor.downsample(voxel_size):
            raise Exception("Error en downsampling")
        
        update_job_status(db, job_id, JobStatus.processing, progress=25)
        
        # Eliminar outliers
        nb_neighbors = kwargs.get('nb_neighbors', 20)
        std_ratio = kwargs.get('std_ratio', 2.0)
        if not processor.remove_outliers(nb_neighbors, std_ratio):
            raise Exception("Error al eliminar outliers")
        
        update_job_status(db, job_id, JobStatus.processing, progress=35)
        
        # Estimar normales
        radius = kwargs.get('normal_radius', 0.1)
        max_nn = kwargs.get('normal_max_nn', 30)
        if not processor.estimate_normals(radius, max_nn):
            raise Exception("Error al estimar normales")
        
        update_job_status(db, job_id, JobStatus.processing, progress=45)
        
        # Reconstrucción según algoritmo seleccionado
        logger.info(f"Aplicando algoritmo {algorithm}...")
        
        if algorithm == 'poisson':
            depth = kwargs.get('poisson_depth', 9)
            width = kwargs.get('poisson_width', 0)
            scale = kwargs.get('poisson_scale', 1.1)
            linear_fit = kwargs.get('poisson_linear_fit', False)
            
            if not processor.reconstruct_poisson(depth, width, scale, linear_fit):
                raise Exception("Error en reconstrucción Poisson")
                
        elif algorithm == 'ball_pivoting':
            radii = kwargs.get('ball_pivoting_radii', None)
            if not processor.reconstruct_ball_pivoting(radii):
                raise Exception("Error en reconstrucción Ball Pivoting")
                
        elif algorithm == 'alpha_shape':
            alpha = kwargs.get('alpha_shape_alpha', 0.1)
            if not processor.reconstruct_alpha_shape(alpha):
                raise Exception("Error en reconstrucción Alpha Shape")
        else:
            raise Exception(f"Algoritmo no soportado: {algorithm}")
        
        update_job_status(db, job_id, JobStatus.processing, progress=70)
        
        # Transferir colores si están disponibles
        logger.info("Transfiriendo colores...")
        processor.transfer_colors()
        
        update_job_status(db, job_id, JobStatus.processing, progress=80)
        
        # Guardar malla
        logger.info("Guardando malla...")
        output_format = kwargs.get('output_format', 'ply')
        output_filename = f"mesh_{job_id}.{output_format}"
        output_path = Path("saas3d/api/outputs") / output_filename
        
        if not processor.save_mesh(str(output_path), output_format):
            raise Exception("Error al guardar la malla")
        
        update_job_status(db, job_id, JobStatus.processing, progress=95)
        
        # Obtener información de la malla
        mesh_info = processor.get_mesh_info()
        
        # Actualizar trabajo como completado
        update_job_status(db, job_id, JobStatus.completed, progress=100, 
                        output_key=output_filename)
        
        logger.info(f"Procesamiento completado para job {job_id}")
        
        result = {
            'success': True,
            'job_id': job_id,
            'output_file': str(output_path),
            'output_filename': output_filename,
            'mesh_info': mesh_info,
            'algorithm_used': algorithm,
            'parameters': kwargs
        }
        
        return result
        
    except Exception as e:
        error_msg = f"Error en procesamiento: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Actualizar trabajo como fallido
        update_job_status(db, job_id, JobStatus.failed, error=error_msg)
        
        return {
            'success': False,
            'job_id': job_id,
            'error': error_msg
        }
        
    finally:
        db.close()

def update_job_status(db, job_id: int, status: JobStatus, progress: int = None, 
                     error: str = None, output_key: str = None):
    """Actualizar estado de un trabajo en la base de datos"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            if progress is not None:
                job.progress = progress
            if error is not None:
                job.error = error
            if output_key is not None:
                job.output_key = output_key
            
            db.commit()
            logger.info(f"Job {job_id} actualizado: {status} ({progress}%)")
        else:
            logger.error(f"Job {job_id} no encontrado")
    except Exception as e:
        logger.error(f"Error al actualizar job {job_id}: {str(e)}")
        db.rollback()

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handler ejecutado antes de cada tarea"""
    logger.info(f"Iniciando tarea {task_id}: {task.name}")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Handler ejecutado después de cada tarea"""
    logger.info(f"Tarea {task_id} completada con estado: {state}")

# Función para iniciar el worker
def start_worker():
    """Iniciar el worker de Celery"""
    logger.info("Iniciando worker de Celery...")
    celery_app.worker_main(['worker', '--loglevel=info', '--concurrency=2'])

if __name__ == '__main__':
    start_worker()
