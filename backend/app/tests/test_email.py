"""Tests for email functionality."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO

from app.services.email.sender import EmailService
from app.services.email.templates import (
    render_template,
    CALCULATION_REPORT_TEMPLATE,
    WELCOME_EMAIL_TEMPLATE,
    ERROR_NOTIFICATION_TEMPLATE,
    MULTI_SITE_REPORT_TEMPLATE,
)


@pytest.fixture
def mock_smtp_settings(monkeypatch):
    """Mock SMTP settings."""
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "test@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("SMTP_FROM", "noreply@test.com")
    monkeypatch.setenv("SMTP_BCC", "sales@test.com")

    # Force reload of settings
    from app.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def email_service(mock_smtp_settings):
    """Create email service instance with mocked settings."""
    return EmailService()


@pytest.fixture
def sample_calculation_data():
    """Sample calculation data for email."""
    return {
        'project': {
            'project_name': 'Test Project',
            'created_by': 'John Doe',
            'creator_email': 'john@example.com',
        },
        'summary': {
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
        },
        'retention_days': 30,
        'warnings': ['Test warning'],
        'errors': [],
    }


class TestEmailTemplates:
    """Test email template rendering."""

    def test_render_calculation_template(self):
        """Test rendering calculation report template."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Test Project',
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
            'retention_days': 30,
            'warnings': [],
            'year': 2025,
        }

        html = render_template(CALCULATION_REPORT_TEMPLATE, context)

        assert 'John Doe' in html
        assert 'Test Project' in html
        assert '100' in html
        assert '1.5 TB' in html
        assert '400.0 Mbps' in html

    def test_render_template_with_warnings(self):
        """Test rendering template with warnings."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Test Project',
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
            'retention_days': 30,
            'warnings': ['Warning 1', 'Warning 2'],
            'year': 2025,
        }

        html = render_template(CALCULATION_REPORT_TEMPLATE, context)

        assert 'Warning 1' in html
        assert 'Warning 2' in html
        assert 'Warnings' in html


class TestEmailService:
    """Test email service functionality."""

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service):
        """Test successful email sending."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
            )

            assert result['success'] is True
            assert 'successfully' in result['message']
            assert mock_send.called

    @pytest.mark.asyncio
    async def test_send_email_with_attachments(self, email_service):
        """Test sending email with attachments."""
        pdf_buffer = BytesIO(b'%PDF-1.4 fake pdf content')

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
                attachments=[{
                    'filename': 'report.pdf',
                    'content': pdf_buffer,
                }],
            )

            assert result['success'] is True
            assert mock_send.called

    @pytest.mark.asyncio
    async def test_send_email_with_cc_bcc(self, email_service):
        """Test sending email with CC and BCC."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
                cc=['cc@example.com'],
                bcc=['bcc@example.com'],
            )

            assert result['success'] is True
            assert len(result['recipients']) == 3  # to + cc + bcc

    @pytest.mark.asyncio
    async def test_send_email_without_credentials(self, monkeypatch):
        """Test sending email without SMTP credentials."""
        # Clear SMTP credentials
        monkeypatch.setenv("SMTP_USER", "")
        monkeypatch.setenv("SMTP_PASSWORD", "")

        # Force reload of settings
        from app.core.config import get_settings
        get_settings.cache_clear()

        # Create service with empty credentials
        service = EmailService()

        result = await service.send_email(
            to=['test@example.com'],
            subject='Test Subject',
            html_body='<p>Test HTML</p>',
            text_body='Test Text',
        )

        assert result['success'] is False
        assert 'credentials not configured' in result['error']

        # Clean up
        get_settings.cache_clear()

    @pytest.mark.asyncio
    async def test_send_email_smtp_error(self, email_service):
        """Test email sending with SMTP error."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception('SMTP connection failed')

            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
            )

            assert result['success'] is False
            assert 'SMTP connection failed' in result['error']

    @pytest.mark.asyncio
    async def test_send_calculation_report(self, email_service, sample_calculation_data):
        """Test sending calculation report email."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_calculation_report(
                recipient_email='customer@example.com',
                recipient_name='John Doe',
                project_name='Test Project',
                calculation_data=sample_calculation_data,
            )

            assert result['success'] is True
            assert mock_send.called

            # Verify BCC was added
            assert 'sales@test.com' in result['recipients']

    @pytest.mark.asyncio
    async def test_send_calculation_report_with_pdf(self, email_service, sample_calculation_data):
        """Test sending calculation report with PDF attachment."""
        pdf_buffer = BytesIO(b'%PDF-1.4 fake pdf content')

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_calculation_report(
                recipient_email='customer@example.com',
                recipient_name='John Doe',
                project_name='Test Project',
                calculation_data=sample_calculation_data,
                pdf_buffer=pdf_buffer,
            )

            assert result['success'] is True
            assert mock_send.called

    @pytest.mark.asyncio
    async def test_send_test_email(self, email_service):
        """Test sending test email."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_test_email(
                recipient_email='test@example.com'
            )

            assert result['success'] is True
            assert mock_send.called

    @pytest.mark.asyncio
    async def test_send_multi_site_report(self, email_service):
        """Test sending multi-site report email."""
        multi_site_data = {
            'summary': {
                'total_sites': 3,
                'total_devices': 5000,
                'total_servers': 20,
                'total_storage_tb': 50.5,
                'total_bitrate_mbps': 2000.0,
            },
            'warnings': [],
            'errors': [],
        }

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_multi_site_report(
                recipient_email='customer@example.com',
                recipient_name='John Doe',
                project_name='Multi-Site Project',
                multi_site_data=multi_site_data,
            )

            assert result['success'] is True
            assert mock_send.called


class TestEmailEdgeCases:
    """Test email edge cases."""

    @pytest.mark.asyncio
    async def test_send_email_multiple_recipients(self, email_service):
        """Test sending email to multiple recipients."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test1@example.com', 'test2@example.com', 'test3@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
            )

            assert result['success'] is True
            assert len(result['recipients']) == 3

    @pytest.mark.asyncio
    async def test_send_email_with_special_characters(self, email_service):
        """Test sending email with special characters in subject and body."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject with émojis 🎉 and spëcial çhars',
                html_body='<p>Test with émojis 🎉</p>',
                text_body='Test with émojis 🎉',
            )

            assert result['success'] is True


class TestEnhancedEmailTemplates:
    """Test enhanced email templates with OEM branding."""

    def test_render_template_with_branding(self):
        """Test rendering template with OEM branding."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Acme Security Project',
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
            'retention_days': 30,
            'warnings': [],
            'year': 2025,
            'company_name': 'Acme Security Systems',
            'logo_url': 'https://example.com/logo.png',
            'primary_color': '#ff6b35',
            'secondary_color': '#f7931e',
            'accent_color': '#c1121f',
            'tagline': 'Securing Your World',
            'website': 'https://acmesecurity.com',
        }

        html = render_template(CALCULATION_REPORT_TEMPLATE, context)

        assert 'Acme Security Systems' in html
        assert 'https://example.com/logo.png' in html
        assert '#ff6b35' in html
        assert '#f7931e' in html
        assert '#c1121f' in html
        assert 'Securing Your World' in html
        assert 'https://acmesecurity.com' in html

    def test_render_welcome_template(self):
        """Test rendering welcome email template."""
        context = {
            'recipient_name': 'Jane Smith',
            'company_name': 'Acme Security',
            'year': 2025,
            'calculator_url': 'https://calculator.acme.com',
            'primary_color': '#ff6b35',
            'secondary_color': '#f7931e',
            'accent_color': '#c1121f',
        }

        html = render_template(WELCOME_EMAIL_TEMPLATE, context)

        assert 'Jane Smith' in html
        assert 'Welcome to Acme Security' in html
        assert 'https://calculator.acme.com' in html
        assert '#ff6b35' in html

    def test_render_error_notification_template(self):
        """Test rendering error notification template."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Test Project',
            'error_message': 'Invalid camera configuration',
            'company_name': 'Network Optix',
            'year': 2025,
        }

        html = render_template(ERROR_NOTIFICATION_TEMPLATE, context)

        assert 'John Doe' in html
        assert 'Test Project' in html
        assert 'Invalid camera configuration' in html
        assert 'Calculation Error' in html

    def test_render_multi_site_template(self):
        """Test rendering multi-site report template."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Multi-Site Deployment',
            'site_count': 3,
            'total_cameras': 300,
            'total_servers': 6,
            'total_storage_tb': 4.5,
            'sites': [
                {
                    'name': 'Site A',
                    'cameras': 100,
                    'servers': 2,
                    'storage_tb': 1.5,
                    'bandwidth_mbps': 400,
                },
                {
                    'name': 'Site B',
                    'cameras': 150,
                    'servers': 3,
                    'storage_tb': 2.0,
                    'bandwidth_mbps': 600,
                },
                {
                    'name': 'Site C',
                    'cameras': 50,
                    'servers': 1,
                    'storage_tb': 1.0,
                    'bandwidth_mbps': 200,
                },
            ],
            'company_name': 'Network Optix',
            'year': 2025,
            'primary_color': '#2563eb',
            'secondary_color': '#3b82f6',
            'accent_color': '#1e40af',
        }

        html = render_template(MULTI_SITE_REPORT_TEMPLATE, context)

        assert 'Multi-Site Deployment' in html
        assert 'Site A' in html
        assert 'Site B' in html
        assert 'Site C' in html
        assert '300' in html  # total cameras
        assert '6' in html    # total servers
        assert '4.5 TB' in html  # total storage

    def test_template_with_default_values(self):
        """Test template rendering with default values."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Test Project',
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
            'retention_days': 30,
            'warnings': [],
            'year': 2025,
        }

        html = render_template(CALCULATION_REPORT_TEMPLATE, context)

        # Should use default values
        assert 'Nx System Calculator' in html or 'Network Optix' in html
        assert '#2563eb' in html  # default primary color

    def test_template_mobile_responsive(self):
        """Test that templates include mobile responsive styles."""
        context = {
            'recipient_name': 'John Doe',
            'project_name': 'Test',
            'total_devices': 100,
            'servers_needed': 2,
            'total_storage_tb': 1.5,
            'total_bitrate_mbps': 400.0,
            'retention_days': 30,
            'warnings': [],
            'year': 2025,
        }

        html = render_template(CALCULATION_REPORT_TEMPLATE, context)

        # Check for media query
        assert '@media' in html
        assert 'max-width: 600px' in html

    @pytest.mark.asyncio
    async def test_send_email_large_attachment(self, email_service):
        """Test sending email with large attachment."""
        # Create a 5MB fake PDF
        large_pdf = BytesIO(b'%PDF-1.4 ' + b'x' * (5 * 1024 * 1024))

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            result = await email_service.send_email(
                to=['test@example.com'],
                subject='Test Subject',
                html_body='<p>Test HTML</p>',
                text_body='Test Text',
                attachments=[{
                    'filename': 'large_report.pdf',
                    'content': large_pdf,
                }],
            )

            assert result['success'] is True

