import open3d as o3d
import numpy as np

def downsample_point_cloud(pcd, voxel_size):
    """
    Realiza downsampling de la nube de puntos usando voxel_size.
    """
    if voxel_size > 0:
        return pcd.voxel_down_sample(voxel_size)
    return pcd

def remove_outliers(pcd, nb_neighbors=20, std_ratio=2.0):
    """
    Elimina outliers estadísticos de la nube de puntos.
    """
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    return pcd 