"""Tests for PDF generation with charts."""

import pytest
import os
import tempfile
from io import BytesIO
from app.services.pdf.generator import PDFGenerator


class TestPDFGeneratorWithCharts:
    """Test PDF generation with chart integration."""

    @pytest.fixture
    def pdf_generator(self):
        """Create PDF generator with charts enabled."""
        return PDFGenerator(include_charts=True)

    @pytest.fixture
    def pdf_generator_no_charts(self):
        """Create PDF generator with charts disabled."""
        return PDFGenerator(include_charts=False)

    @pytest.fixture
    def sample_calculation_data(self):
        """Sample calculation data for PDF generation."""
        return {
            'project': {
                'project_name': 'Test Project',
                'created_by': 'Test User',
                'creator_email': 'test@example.com',
                'description': 'Test project description',
            },
            'summary': {
                'total_devices': 100,
                'servers_needed': 2,
                'total_storage_tb': 1.5,
                'total_bitrate_mbps': 200.0,
                'servers_with_failover': 3,
            },
            'storage': {
                'total_storage_gb': 1500.0,
                'total_storage_tb': 1.5,
                'raid_overhead_gb': 375.0,
                'daily_storage_gb': 50.0,
                'raw_storage_needed_gb': 1875.0,
                'usable_storage_gb': 1500.0,
            },
            'servers': {
                'servers_needed': 2,
                'servers_with_failover': 3,
                'devices_per_server': 50,
                'bitrate_per_server_mbps': 100.0,
                'limiting_factor': 'device_count',
                'recommended_tier': {
                    'tier': 'medium',
                    'cpu': 'Intel Xeon E5-2680',
                    'ram_gb': 64,
                    'storage_type': 'SSD',
                },
            },
            'bandwidth': {
                'total_bitrate_mbps': 200.0,
                'total_bitrate_gbps': 0.2,
                'per_server_mbps': 100.0,
                'nic_utilization_percentage': 10.0,
            },
            'licenses': {
                'professional_licenses': 100,
                'total_licenses': 100,
                'licensing_model': 'per_device',
            },
            'camera_groups': [
                {
                    'resolution_id': '2mp_1080p',
                    'num_cameras': 50,
                    'bitrate_kbps': 2000,
                },
                {
                    'resolution_id': '4mp',
                    'num_cameras': 50,
                    'bitrate_kbps': 3000,
                },
            ],
            'retention_days': 30,
            'warnings': ['Test warning'],
            'errors': [],
        }

    def test_pdf_generation_with_charts(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with charts enabled."""
        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        assert isinstance(buffer, BytesIO)

        # Check buffer has content (seek to end to get size)
        buffer.seek(0, 2)  # Seek to end
        size = buffer.tell()
        buffer.seek(0)  # Seek back to start
        assert size > 0

        # Verify temp files were cleaned up
        assert len(pdf_generator.temp_chart_files) == 0

    def test_pdf_generation_without_charts(self, pdf_generator_no_charts, sample_calculation_data):
        """Test PDF generation with charts disabled."""
        buffer = pdf_generator_no_charts.generate_report(sample_calculation_data)

        assert buffer is not None
        assert isinstance(buffer, BytesIO)

        # Check buffer has content
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_save_to_file_with_charts(self, pdf_generator, sample_calculation_data):
        """Test saving PDF to file with charts."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name

        try:
            buffer = pdf_generator.generate_report(
                sample_calculation_data,
                output_path=output_path
            )

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_pdf_with_company_branding(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with company branding."""
        buffer = pdf_generator.generate_report(
            sample_calculation_data,
            company_name="Test Company"
        )

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_with_minimal_data(self, pdf_generator):
        """Test PDF generation with minimal data."""
        minimal_data = {
            'project': {
                'project_name': 'Minimal Project',
                'created_by': 'User',
                'creator_email': 'user@example.com',
            },
            'summary': {
                'total_devices': 10,
                'servers_needed': 1,
                'total_storage_tb': 0.1,
                'total_bitrate_mbps': 20.0,
            },
            'storage': {},
            'servers': {},
            'bandwidth': {},
            'licenses': {},
            'camera_groups': [],
            'retention_days': 30,
        }

        buffer = pdf_generator.generate_report(minimal_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_with_empty_camera_groups(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with empty camera groups."""
        sample_calculation_data['camera_groups'] = []

        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_with_zero_storage(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with zero storage."""
        sample_calculation_data['storage'] = {
            'total_storage_gb': 0.0,
            'raid_overhead_gb': 0.0,
            'daily_storage_gb': 0.0,
        }

        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_temp_file_cleanup(self, pdf_generator, sample_calculation_data):
        """Test that temporary chart files are cleaned up."""
        # Generate PDF
        buffer = pdf_generator.generate_report(sample_calculation_data)

        # Verify temp files list is empty after generation
        assert len(pdf_generator.temp_chart_files) == 0

    def test_multiple_pdf_generations(self, pdf_generator, sample_calculation_data):
        """Test generating multiple PDFs sequentially."""
        for i in range(3):
            buffer = pdf_generator.generate_report(sample_calculation_data)
            assert buffer is not None
            buffer.seek(0, 2)
            assert buffer.tell() > 0
            buffer.seek(0)
            assert len(pdf_generator.temp_chart_files) == 0

    def test_pdf_with_long_retention(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with long retention period."""
        sample_calculation_data['retention_days'] = 365

        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_with_warnings_and_errors(self, pdf_generator, sample_calculation_data):
        """Test PDF generation with warnings and errors."""
        sample_calculation_data['warnings'] = [
            'Warning 1: High bitrate detected',
            'Warning 2: Storage capacity near limit',
        ]
        sample_calculation_data['errors'] = [
            'Error 1: Invalid configuration',
        ]

        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

    def test_pdf_chart_generation_failure_handling(self, pdf_generator, sample_calculation_data):
        """Test PDF generation handles chart failures gracefully."""
        # Use invalid data that might cause chart generation issues
        sample_calculation_data['storage'] = {}  # Empty dict instead of None

        # Should still generate PDF without crashing
        buffer = pdf_generator.generate_report(sample_calculation_data)

        assert buffer is not None
        buffer.seek(0, 2)
        assert buffer.tell() > 0
        buffer.seek(0)

