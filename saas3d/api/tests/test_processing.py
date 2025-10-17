"""
Tests para el módulo de procesamiento 3D
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

from processing.point_cloud_processor import PointCloudProcessor

class TestPointCloudProcessor:
    """Tests para PointCloudProcessor"""
    
    def test_init(self):
        """Test inicialización del procesador"""
        processor = PointCloudProcessor()
        assert processor.point_cloud is None
        assert processor.mesh is None
    
    def test_load_point_cloud_ply(self):
        """Test carga de archivo PLY"""
        processor = PointCloudProcessor()
        
        # Crear un archivo PLY temporal
        with tempfile.NamedTemporaryFile(suffix='.ply', delete=False) as tmp_file:
            # Crear un punto simple
            points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
            colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            
            # Escribir header PLY básico
            ply_content = """ply
format ascii 1.0
element vertex 3
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
0.0 0.0 0.0 255 0 0
1.0 0.0 0.0 0 255 0
0.0 1.0 0.0 0 0 255
"""
            tmp_file.write(ply_content.encode())
            tmp_file.flush()
            
            # Test carga
            result = processor.load_point_cloud(tmp_file.name)
            assert result is True
            assert processor.point_cloud is not None
            assert len(processor.point_cloud.points) == 3
            
            # Limpiar
            Path(tmp_file.name).unlink()
    
    def test_load_point_cloud_invalid_file(self):
        """Test carga de archivo inválido"""
        processor = PointCloudProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"not a point cloud")
            tmp_file.flush()
            
            result = processor.load_point_cloud(tmp_file.name)
            assert result is False
            
            Path(tmp_file.name).unlink()
    
    def test_downsample(self):
        """Test downsampling"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        processor.point_cloud.points = [Mock() for _ in range(100)]
        processor.point_cloud.voxel_down_sample.return_value = Mock()
        processor.point_cloud.voxel_down_sample.return_value.points = [Mock() for _ in range(50)]
        
        result = processor.downsample(0.01)
        assert result is True
        processor.point_cloud.voxel_down_sample.assert_called_once_with(0.01)
    
    def test_remove_outliers(self):
        """Test eliminación de outliers"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        processor.point_cloud.points = [Mock() for _ in range(100)]
        processor.point_cloud.remove_statistical_outlier.return_value = (Mock(), [])
        processor.point_cloud.remove_statistical_outlier.return_value[0].points = [Mock() for _ in range(90)]
        
        result = processor.remove_outliers(20, 2.0)
        assert result is True
        processor.point_cloud.remove_statistical_outlier.assert_called_once_with(
            nb_neighbors=20, std_ratio=2.0
        )
    
    def test_estimate_normals(self):
        """Test estimación de normales"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        processor.point_cloud.estimate_normals = Mock()
        processor.point_cloud.normalize_normals = Mock()
        
        result = processor.estimate_normals(0.1, 30)
        assert result is True
        processor.point_cloud.estimate_normals.assert_called_once()
        processor.point_cloud.normalize_normals.assert_called_once()
    
    @patch('processing.point_cloud_processor.o3d')
    def test_reconstruct_poisson(self, mock_o3d):
        """Test reconstrucción Poisson"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        processor.point_cloud.create_mesh_poisson.return_value = (Mock(), Mock())
        
        # Mock mesh
        mock_mesh = Mock()
        mock_mesh.vertices = [Mock() for _ in range(100)]
        processor.point_cloud.create_mesh_poisson.return_value = (mock_mesh, Mock())
        
        result = processor.reconstruct_poisson(9, 0, 1.1, False)
        assert result is True
        processor.point_cloud.create_mesh_poisson.assert_called_once_with(
            depth=9, width=0, scale=1.1, linear_fit=False
        )
    
    @patch('processing.point_cloud_processor.o3d')
    def test_reconstruct_ball_pivoting(self, mock_o3d):
        """Test reconstrucción Ball Pivoting"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        processor.point_cloud.compute_nearest_neighbor_distance.return_value = [0.01, 0.02, 0.01]
        
        # Mock mesh creation
        mock_mesh = Mock()
        mock_mesh.vertices = [Mock() for _ in range(50)]
        mock_o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting.return_value = mock_mesh
        
        result = processor.reconstruct_ball_pivoting()
        assert result is True
    
    @patch('processing.point_cloud_processor.o3d')
    def test_reconstruct_alpha_shape(self, mock_o3d):
        """Test reconstrucción Alpha Shape"""
        processor = PointCloudProcessor()
        
        # Mock point cloud
        processor.point_cloud = Mock()
        
        # Mock mesh creation
        mock_mesh = Mock()
        mock_mesh.vertices = [Mock() for _ in range(30)]
        mock_o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape.return_value = mock_mesh
        
        result = processor.reconstruct_alpha_shape(0.1)
        assert result is True
    
    def test_transfer_colors(self):
        """Test transferencia de colores"""
        processor = PointCloudProcessor()
        
        # Mock point cloud y mesh
        processor.point_cloud = Mock()
        processor.point_cloud.has_colors.return_value = True
        processor.point_cloud.colors = [Mock() for _ in range(3)]
        
        processor.mesh = Mock()
        processor.mesh.vertices = [Mock() for _ in range(3)]
        
        # Mock KDTree
        mock_tree = Mock()
        mock_tree.search_knn_vector_3d.return_value = [None, [0], None]
        
        with patch('processing.point_cloud_processor.o3d.geometry.KDTreeFlann', return_value=mock_tree):
            result = processor.transfer_colors()
            assert result is True
    
    def test_save_mesh(self):
        """Test guardado de malla"""
        processor = PointCloudProcessor()
        
        # Mock mesh
        processor.mesh = Mock()
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "test_mesh.ply"
            
            with patch('processing.point_cloud_processor.o3d.io.write_triangle_mesh', return_value=True):
                result = processor.save_mesh(str(output_path), 'ply')
                assert result is True
    
    def test_get_mesh_info(self):
        """Test obtención de información de malla"""
        processor = PointCloudProcessor()
        
        # Sin malla
        info = processor.get_mesh_info()
        assert info == {}
        
        # Con malla
        processor.mesh = Mock()
        processor.mesh.vertices = [Mock() for _ in range(100)]
        processor.mesh.triangles = [Mock() for _ in range(200)]
        processor.mesh.has_vertex_colors.return_value = True
        processor.mesh.has_vertex_normals.return_value = False
        
        info = processor.get_mesh_info()
        assert info['vertices'] == 100
        assert info['triangles'] == 200
        assert info['has_colors'] is True
        assert info['has_normals'] is False
