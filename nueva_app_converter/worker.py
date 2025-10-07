import open3d as o3d
from procesado.preprocesado import downsample_point_cloud, remove_outliers
from procesado.reconstruccion import reconstruir_poisson, reconstruir_ball_pivoting, reconstruir_alpha_shape
from procesado.color import transferir_color
from utils.io import leer_nube
import numpy as np
import tempfile
import os

def conversion_worker(params, queue):
    try:
        queue.put({'progress': 5, 'status': 'Cargando nube de puntos...'})
        pcd = leer_nube(params['input_file'])
        queue.put({'progress': 20, 'status': 'Preprocesando nube...'})
        pcd = downsample_point_cloud(pcd, params['voxel'])
        if params['eliminar_outliers']:
            pcd = remove_outliers(pcd, nb_neighbors=params['nb_neighbors'], std_ratio=params['std_ratio'])
        # --- Preprocesado extra ---
        pcd.remove_duplicated_points()
        pts = np.asarray(pcd.points)
        centro = pts.mean(axis=0)
        pcd.points = o3d.utility.Vector3dVector(pts - centro)
        print(f'Nº de puntos tras preprocesado: {len(pcd.points)}')
        print('Mínimo:', pts.min(axis=0))
        print('Máximo:', pts.max(axis=0))
        # --- Fin preprocesado extra ---
        queue.put({'progress': 30, 'status': 'Calculando normales...'})
        pcd.estimate_normals()
        pcd.orient_normals_consistent_tangent_plane(100)
        queue.put({'progress': 50, 'status': 'Reconstruyendo malla...'})
        metodo = params['metodo']
        if metodo == "poisson":
            mesh = reconstruir_poisson(pcd, depth=params['param'], density_percentile=params['dens'])
        elif metodo == "ball_pivoting":
            mesh = reconstruir_ball_pivoting(pcd, radio=params['param']/100.0)
        elif metodo == "alpha_shape":
            mesh = reconstruir_alpha_shape(pcd, alpha=params['param']/100.0)
        else:
            queue.put({'result': (None, None, "Método de reconstrucción no soportado.")})
            return
        queue.put({'progress': 70, 'status': 'Transfiriendo color...'})
        mesh = transferir_color(mesh, pcd, metodo=params['color_method'], k_neighbors=params['k'])
        if params['eliminar_fragmentos']:
            queue.put({'progress': 85, 'status': 'Eliminando fragmentos pequeños...'})
            mesh = eliminar_componentes_pequenas_worker(mesh, params['min_comp'])
        if params['suavizar']:
            queue.put({'progress': 95, 'status': 'Suavizando malla...'})
            mesh = mesh.filter_smooth_simple(number_of_iterations=1)
        # Guardar malla y nube en archivos temporales
        mesh_fd, mesh_path = tempfile.mkstemp(suffix='.ply')
        os.close(mesh_fd)
        o3d.io.write_triangle_mesh(mesh_path, mesh)
        pcd_fd, pcd_path = tempfile.mkstemp(suffix='.pcd')
        os.close(pcd_fd)
        o3d.io.write_point_cloud(pcd_path, pcd)
        queue.put({'progress': 100, 'status': 'Conversión completada.'})
        queue.put({'result': (mesh_path, pcd_path, "")})
    except Exception as e:
        queue.put({'result': (None, None, str(e))})

def eliminar_componentes_pequenas_worker(mesh, min_triangles=1000):
    mesh = mesh.remove_unreferenced_vertices()
    triangle_clusters, cluster_n_triangles, _ = mesh.cluster_connected_triangles()
    triangle_clusters = np.asarray(triangle_clusters)
    cluster_n_triangles = np.asarray(cluster_n_triangles)
    large_clusters = [i for i, n in enumerate(cluster_n_triangles) if n > min_triangles]
    triangles_to_remove = [i for i, c in enumerate(triangle_clusters) if c not in large_clusters]
    mesh.remove_triangles_by_index(triangles_to_remove)
    mesh.remove_unreferenced_vertices()
    return mesh 