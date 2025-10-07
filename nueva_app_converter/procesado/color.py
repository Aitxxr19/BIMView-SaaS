import open3d as o3d
import numpy as np

def transferir_color(mesh, pcd, metodo='nearest', k_neighbors=10):
    """
    Transfiere el color de la nube de puntos a la malla usando el método seleccionado.
    """
    # Implementación simple: nearest neighbor
    if not pcd.has_colors():
        return mesh
    pcd_tree = o3d.geometry.KDTreeFlann(pcd)
    mesh_colors = []
    for v in np.asarray(mesh.vertices):
        _, idx, _ = pcd_tree.search_knn_vector_3d(v, 1)
        mesh_colors.append(np.asarray(pcd.colors)[idx[0]])
    mesh.vertex_colors = o3d.utility.Vector3dVector(mesh_colors)
    return mesh 