"""Tests for chart generation."""

import pytest
import os
import tempfile
from app.services.pdf.charts import ChartGenerator


class TestChartGenerator:
    """Test chart generation functionality."""
    
    @pytest.fixture
    def chart_generator(self):
        """Create chart generator instance."""
        return ChartGenerator()
    
    @pytest.fixture
    def sample_storage_data(self):
        """Sample storage data for testing."""
        return {
            'total_storage_gb': 1000.0,
            'total_storage_tb': 0.98,
            'raid_overhead_gb': 250.0,
            'daily_storage_gb': 33.33,
            'raw_storage_needed_gb': 1250.0,
        }
    
    @pytest.fixture
    def sample_camera_groups(self):
        """Sample camera groups for testing."""
        return [
            {
                'resolution_id': '2mp_1080p',
                'num_cameras': 50,
                'bitrate_kbps': 2000,
            },
            {
                'resolution_id': '4mp',
                'num_cameras': 30,
                'bitrate_kbps': 3000,
            },
            {
                'resolution_id': '8mp_4k',
                'num_cameras': 20,
                'bitrate_kbps': 5000,
            },
        ]
    
    @pytest.fixture
    def sample_server_data(self):
        """Sample server data for testing."""
        return {
            'servers_needed': 2,
            'servers_with_failover': 3,
            'devices_per_server': 50,
            'bitrate_per_server_mbps': 150.0,
            'limiting_factor': 'device_count',
        }
    
    @pytest.fixture
    def sample_codec_data(self):
        """Sample codec comparison data."""
        return [
            {'codec': 'H.264', 'bitrate_mbps': 200.0, 'storage_tb': 1.5},
            {'codec': 'H.265', 'bitrate_mbps': 100.0, 'storage_tb': 0.75},
        ]
    
    def test_chart_generator_initialization(self, chart_generator):
        """Test chart generator initializes correctly."""
        assert chart_generator is not None
        assert hasattr(chart_generator, 'COLORS')
        assert 'primary' in chart_generator.COLORS
    
    def test_storage_breakdown_chart(self, chart_generator, sample_storage_data):
        """Test storage breakdown chart generation."""
        chart_path = chart_generator.generate_storage_breakdown_chart(sample_storage_data)
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        
        # Cleanup
        os.remove(chart_path)
    
    def test_bitrate_distribution_chart(self, chart_generator, sample_camera_groups):
        """Test bitrate distribution chart generation."""
        chart_path = chart_generator.generate_bitrate_distribution_chart(sample_camera_groups)
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        
        # Cleanup
        os.remove(chart_path)
    
    def test_server_capacity_chart(self, chart_generator, sample_server_data):
        """Test server capacity chart generation."""
        chart_path = chart_generator.generate_server_capacity_chart(sample_server_data)
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        
        # Cleanup
        os.remove(chart_path)
    
    def test_storage_timeline_chart(self, chart_generator, sample_storage_data):
        """Test storage timeline chart generation."""
        retention_days = 30
        chart_path = chart_generator.generate_storage_timeline_chart(
            sample_storage_data, retention_days
        )
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        
        # Cleanup
        os.remove(chart_path)
    
    def test_codec_comparison_chart(self, chart_generator, sample_codec_data):
        """Test codec comparison chart generation."""
        chart_path = chart_generator.generate_codec_comparison_chart(sample_codec_data)
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        
        # Cleanup
        os.remove(chart_path)
    
    def test_chart_with_custom_output_path(self, chart_generator, sample_storage_data):
        """Test chart generation with custom output path."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            chart_path = chart_generator.generate_storage_breakdown_chart(
                sample_storage_data, output_path=output_path
            )
            
            assert chart_path == output_path
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_empty_camera_groups(self, chart_generator):
        """Test chart generation with empty camera groups."""
        chart_path = chart_generator.generate_bitrate_distribution_chart([])
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        
        # Cleanup
        os.remove(chart_path)
    
    def test_zero_storage_data(self, chart_generator):
        """Test chart generation with zero storage."""
        storage_data = {
            'total_storage_gb': 0.0,
            'raid_overhead_gb': 0.0,
            'daily_storage_gb': 0.0,
        }
        
        chart_path = chart_generator.generate_storage_breakdown_chart(storage_data)
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        
        # Cleanup
        os.remove(chart_path)
    
    def test_storage_timeline_long_retention(self, chart_generator, sample_storage_data):
        """Test storage timeline with long retention period."""
        retention_days = 365
        chart_path = chart_generator.generate_storage_timeline_chart(
            sample_storage_data, retention_days
        )
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        
        # Cleanup
        os.remove(chart_path)
    
    def test_multiple_charts_sequential(self, chart_generator, sample_storage_data, 
                                       sample_camera_groups, sample_server_data):
        """Test generating multiple charts sequentially."""
        chart_paths = []
        
        try:
            # Generate multiple charts
            chart_paths.append(
                chart_generator.generate_storage_breakdown_chart(sample_storage_data)
            )
            chart_paths.append(
                chart_generator.generate_bitrate_distribution_chart(sample_camera_groups)
            )
            chart_paths.append(
                chart_generator.generate_server_capacity_chart(sample_server_data)
            )
            
            # Verify all charts exist
            for path in chart_paths:
                assert os.path.exists(path)
                assert path.endswith('.png')
        finally:
            # Cleanup
            for path in chart_paths:
                if os.path.exists(path):
                    os.remove(path)

