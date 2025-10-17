"""
Módulo de procesamiento 3D para conversión de nubes de puntos a mallas
Basado en el código original de nueva_app_converter
"""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

# Importar Open3D de forma opcional
try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    o3d = None

logger = logging.getLogger(__name__)

class PointCloudProcessor:
    """Procesador de nubes de puntos para conversión a mallas 3D"""
    
    def __init__(self):
        self.point_cloud = None
        self.mesh = None
        
    def load_point_cloud(self, file_path: str) -> bool:
        """Cargar nube de puntos desde archivo"""
        if not OPEN3D_AVAILABLE:
            logger.error("Open3D no está disponible. Instalar con: pip install open3d")
            return False
            
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.ply':
                self.point_cloud = o3d.io.read_point_cloud(str(file_path))
            elif file_path.suffix.lower() in ['.las', '.laz']:
                # Para archivos LAS/LAZ necesitamos usar laspy
                import laspy
                las = laspy.read(str(file_path))
                points = np.vstack((las.x, las.y, las.z)).transpose()
                self.point_cloud = o3d.geometry.PointCloud()
                self.point_cloud.points = o3d.utility.Vector3dVector(points)
                
                # Añadir colores si están disponibles
                if hasattr(las, 'red') and hasattr(las, 'green') and hasattr(las, 'blue'):
                    colors = np.vstack((las.red, las.green, las.blue)).transpose()
                    colors = colors / 65535.0  # Normalizar a [0,1]
                    self.point_cloud.colors = o3d.utility.Vector3dVector(colors)
            elif file_path.suffix.lower() == '.pcd':
                self.point_cloud = o3d.io.read_point_cloud(str(file_path))
            elif file_path.suffix.lower() == '.xyz':
                self.point_cloud = o3d.io.read_point_cloud(str(file_path))
            else:
                logger.error(f"Formato de archivo no soportado: {file_path.suffix}")
                return False
                
            if len(self.point_cloud.points) == 0:
                logger.error("La nube de puntos está vacía")
                return False
                
            logger.info(f"Nube de puntos cargada: {len(self.point_cloud.points)} puntos")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar nube de puntos: {str(e)}")
            return False
    
    def downsample(self, voxel_size: float = 0.01) -> bool:
        """Reducir densidad de puntos"""
        if not OPEN3D_AVAILABLE:
            logger.error("Open3D no está disponible")
            return False
            
        try:
            if self.point_cloud is None:
                return False
                
            original_count = len(self.point_cloud.points)
            self.point_cloud = self.point_cloud.voxel_down_sample(voxel_size)
            new_count = len(self.point_cloud.points)
            
            logger.info(f"Downsampling: {original_count} -> {new_count} puntos")
            return True
            
        except Exception as e:
            logger.error(f"Error en downsampling: {str(e)}")
            return False
    
    def remove_outliers(self, nb_neighbors: int = 20, std_ratio: float = 2.0) -> bool:
        """Eliminar puntos atípicos"""
        try:
            if self.point_cloud is None:
                return False
                
            original_count = len(self.point_cloud.points)
            self.point_cloud, _ = self.point_cloud.remove_statistical_outlier(
                nb_neighbors=nb_neighbors, std_ratio=std_ratio
            )
            new_count = len(self.point_cloud.points)
            
            logger.info(f"Outlier removal: {original_count} -> {new_count} puntos")
            return True
            
        except Exception as e:
            logger.error(f"Error en eliminación de outliers: {str(e)}")
            return False
    
    def estimate_normals(self, radius: float = 0.1, max_nn: int = 30) -> bool:
        """Estimar normales de la superficie"""
        try:
            if self.point_cloud is None:
                return False
                
            self.point_cloud.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn)
            )
            self.point_cloud.normalize_normals()
            
            logger.info("Normales estimadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al estimar normales: {str(e)}")
            return False
    
    def reconstruct_poisson(self, depth: int = 9, width: int = 0, scale: float = 1.1, 
                          linear_fit: bool = False) -> bool:
        """Reconstrucción usando algoritmo Poisson"""
        try:
            if self.point_cloud is None:
                return False
                
            logger.info("Iniciando reconstrucción Poisson...")
            self.mesh, _ = self.point_cloud.create_mesh_poisson(
                depth=depth, width=width, scale=scale, linear_fit=linear_fit
            )
            
            if len(self.mesh.vertices) == 0:
                logger.error("La reconstrucción Poisson falló")
                return False
                
            logger.info(f"Reconstrucción Poisson completada: {len(self.mesh.vertices)} vértices")
            return True
            
        except Exception as e:
            logger.error(f"Error en reconstrucción Poisson: {str(e)}")
            return False
    
    def reconstruct_ball_pivoting(self, radii: list = None) -> bool:
        """Reconstrucción usando algoritmo Ball Pivoting"""
        try:
            if self.point_cloud is None:
                return False
                
            if radii is None:
                distances = self.point_cloud.compute_nearest_neighbor_distance()
                avg_dist = np.mean(distances)
                radii = [avg_dist, avg_dist * 2]
                
            logger.info("Iniciando reconstrucción Ball Pivoting...")
            self.mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                self.point_cloud, o3d.utility.DoubleVector(radii)
            )
            
            if len(self.mesh.vertices) == 0:
                logger.error("La reconstrucción Ball Pivoting falló")
                return False
                
            logger.info(f"Reconstrucción Ball Pivoting completada: {len(self.mesh.vertices)} vértices")
            return True
            
        except Exception as e:
            logger.error(f"Error en reconstrucción Ball Pivoting: {str(e)}")
            return False
    
    def reconstruct_alpha_shape(self, alpha: float = 0.1) -> bool:
        """Reconstrucción usando algoritmo Alpha Shape"""
        try:
            if self.point_cloud is None:
                return False
                
            logger.info("Iniciando reconstrucción Alpha Shape...")
            self.mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
                self.point_cloud, alpha
            )
            
            if len(self.mesh.vertices) == 0:
                logger.error("La reconstrucción Alpha Shape falló")
                return False
                
            logger.info(f"Reconstrucción Alpha Shape completada: {len(self.mesh.vertices)} vértices")
            return True
            
        except Exception as e:
            logger.error(f"Error en reconstrucción Alpha Shape: {str(e)}")
            return False
    
    def transfer_colors(self) -> bool:
        """Transferir colores de la nube de puntos a la malla"""
        try:
            if self.point_cloud is None or self.mesh is None:
                return False
                
            if not self.point_cloud.has_colors():
                logger.warning("La nube de puntos no tiene colores")
                return False
                
            # Crear KDTree para búsqueda rápida
            pcd_tree = o3d.geometry.KDTreeFlann(self.point_cloud)
            
            # Obtener vértices de la malla
            mesh_vertices = np.asarray(self.mesh.vertices)
            mesh_colors = np.zeros((len(mesh_vertices), 3))
            
            # Para cada vértice de la malla, encontrar el punto más cercano
            for i, vertex in enumerate(mesh_vertices):
                [_, idx, _] = pcd_tree.search_knn_vector_3d(vertex, 1)
                mesh_colors[i] = self.point_cloud.colors[idx[0]]
            
            self.mesh.vertex_colors = o3d.utility.Vector3dVector(mesh_colors)
            logger.info("Colores transferidos a la malla")
            return True
            
        except Exception as e:
            logger.error(f"Error al transferir colores: {str(e)}")
            return False
    
    def save_mesh(self, output_path: str, format: str = 'ply') -> bool:
        """Guardar malla en archivo"""
        try:
            if self.mesh is None:
                return False
                
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'ply':
                success = o3d.io.write_triangle_mesh(str(output_path), self.mesh)
            elif format.lower() == 'obj':
                success = o3d.io.write_triangle_mesh(str(output_path), self.mesh)
            elif format.lower() == 'stl':
                success = o3d.io.write_triangle_mesh(str(output_path), self.mesh)
            else:
                logger.error(f"Formato de salida no soportado: {format}")
                return False
                
            if success:
                logger.info(f"Malla guardada en: {output_path}")
                return True
            else:
                logger.error("Error al guardar la malla")
                return False
                
        except Exception as e:
            logger.error(f"Error al guardar malla: {str(e)}")
            return False
    
    def get_mesh_info(self) -> dict:
        """Obtener información de la malla generada"""
        if self.mesh is None:
            return {}
            
        return {
            'vertices': len(self.mesh.vertices),
            'triangles': len(self.mesh.triangles),
            'has_colors': self.mesh.has_vertex_colors(),
            'has_normals': self.mesh.has_vertex_normals()
        }
