import open3d as o3d
import numpy as np

def reconstruir_poisson(pcd, depth=9, density_percentile=0.01):
    """
    Reconstruye una malla usando Poisson y filtra por densidad.
    """
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=depth)
    if densities is not None and density_percentile > 0:
        densities = np.asarray(densities)
        threshold = np.quantile(densities, density_percentile)
        mesh.remove_vertices_by_mask(densities < threshold)
    return mesh

def reconstruir_ball_pivoting(pcd, radio=0.05):
    """
    Reconstruye una malla usando Ball Pivoting con un radio dado.
    """
    radii = [radio, radio * 2, radio * 3]
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd, o3d.utility.DoubleVector(radii)
    )
    return mesh

def reconstruir_alpha_shape(pcd, alpha=0.05):
    """
    Reconstruye una malla usando Alpha Shape con un valor alpha dado.
    """
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
    return mesh 