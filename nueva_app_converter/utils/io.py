import open3d as o3d
import laspy
import numpy as np

def leer_nube(file_path):
    """
    Lee una nube de puntos desde archivo (soporta .las, .laz, .ply, .pcd, .xyz).
    """
    ext = file_path.lower().split('.')[-1]
    if ext in ['las', 'laz']:
        las = laspy.read(file_path)
        points = np.vstack((las.x, las.y, las.z)).T
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        if hasattr(las, 'red'):
            colors = np.vstack((las.red, las.green, las.blue)).T / 65535.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        return pcd
    else:
        return o3d.io.read_point_cloud(file_path)

def guardar_malla(mesh, file_path):
    """
    Guarda la malla en el formato especificado (.ply, .obj, .stl).
    """
    return o3d.io.write_triangle_mesh(file_path, mesh) 