"""Email sending service using SMTP."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any
from datetime import datetime
from io import BytesIO

from app.core.config import get_settings
from app.services.email.templates import (
    CALCULATION_REPORT_TEMPLATE,
    CALCULATION_REPORT_TEXT,
    TEST_EMAIL_TEMPLATE,
    TEST_EMAIL_TEXT,
    render_template,
)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with settings."""
        self.settings = get_settings()
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send email via SMTP.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            attachments: List of attachments with 'filename' and 'content' (BytesIO)
        
        Returns:
            Dict with success status and message
        """
        try:
            # Validate SMTP configuration
            if not self.settings.smtp_user or not self.settings.smtp_password:
                return {
                    "success": False,
                    "error": "SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD."
                }
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.settings.smtp_from
            message['To'] = ', '.join(to)
            
            if cc:
                message['Cc'] = ', '.join(cc)
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    filename = attachment.get('filename', 'attachment.pdf')
                    content = attachment.get('content')
                    
                    if isinstance(content, BytesIO):
                        content.seek(0)
                        file_data = content.read()
                    else:
                        file_data = content
                    
                    part = MIMEApplication(file_data, Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
            
            # Prepare recipient list (including BCC)
            all_recipients = to.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                username=self.settings.smtp_user,
                password=self.settings.smtp_password,
                start_tls=True,
            )
            
            return {
                "success": True,
                "message": f"Email sent successfully to {len(all_recipients)} recipient(s)",
                "recipients": all_recipients,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    async def send_calculation_report(
        self,
        recipient_email: str,
        recipient_name: str,
        project_name: str,
        calculation_data: Dict[str, Any],
        pdf_buffer: Optional[BytesIO] = None,
        cc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send calculation report email with PDF attachment.
        
        Args:
            recipient_email: Recipient email address
            recipient_name: Recipient name
            project_name: Project name
            calculation_data: Calculation results
            pdf_buffer: PDF report as BytesIO buffer
            cc: Additional CC recipients
        
        Returns:
            Dict with success status and message
        """
        # Extract summary data
        summary = calculation_data.get('summary', {})
        
        # Prepare template context
        context = {
            'recipient_name': recipient_name,
            'project_name': project_name,
            'total_devices': summary.get('total_devices', 0),
            'servers_needed': summary.get('servers_needed', 0),
            'total_storage_tb': round(summary.get('total_storage_tb', 0), 2),
            'total_bitrate_mbps': round(summary.get('total_bitrate_mbps', 0), 2),
            'retention_days': calculation_data.get('retention_days', 30),
            'warnings': calculation_data.get('warnings', []),
            'year': datetime.now().year,
        }
        
        # Render email templates
        html_body = render_template(CALCULATION_REPORT_TEMPLATE, context)
        text_body = render_template(CALCULATION_REPORT_TEXT, context)
        
        # Prepare attachments
        attachments = []
        if pdf_buffer:
            attachments.append({
                'filename': f'{project_name.replace(" ", "_")}_Report.pdf',
                'content': pdf_buffer,
            })
        
        # Add BCC to sales if configured
        bcc = []
        if self.settings.smtp_bcc:
            bcc.append(self.settings.smtp_bcc)
        
        # Send email
        return await self.send_email(
            to=[recipient_email],
            subject=f'Nx System Calculator Report - {project_name}',
            html_body=html_body,
            text_body=text_body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )
    
    async def send_test_email(
        self,
        recipient_email: str,
    ) -> Dict[str, Any]:
        """
        Send test email to verify SMTP configuration.
        
        Args:
            recipient_email: Test recipient email address
        
        Returns:
            Dict with success status and message
        """
        context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        }
        
        html_body = render_template(TEST_EMAIL_TEMPLATE, context)
        text_body = render_template(TEST_EMAIL_TEXT, context)
        
        return await self.send_email(
            to=[recipient_email],
            subject='Nx System Calculator - Email Test',
            html_body=html_body,
            text_body=text_body,
        )
    
    async def send_multi_site_report(
        self,
        recipient_email: str,
        recipient_name: str,
        project_name: str,
        multi_site_data: Dict[str, Any],
        pdf_buffer: Optional[BytesIO] = None,
        cc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send multi-site calculation report email with PDF attachment.
        
        Args:
            recipient_email: Recipient email address
            recipient_name: Recipient name
            project_name: Project name
            multi_site_data: Multi-site calculation results
            pdf_buffer: PDF report as BytesIO buffer
            cc: Additional CC recipients
        
        Returns:
            Dict with success status and message
        """
        # Extract summary data
        summary = multi_site_data.get('summary', {})
        
        # Prepare template context
        context = {
            'recipient_name': recipient_name,
            'project_name': project_name,
            'total_devices': summary.get('total_devices', 0),
            'servers_needed': summary.get('total_servers', 0),
            'total_storage_tb': round(summary.get('total_storage_tb', 0), 2),
            'total_bitrate_mbps': round(summary.get('total_bitrate_mbps', 0), 2),
            'retention_days': 30,  # Default, could be passed in
            'warnings': multi_site_data.get('warnings', []),
            'year': datetime.now().year,
        }
        
        # Add multi-site specific info
        context['total_sites'] = summary.get('total_sites', 0)
        
        # Render email templates
        html_body = render_template(CALCULATION_REPORT_TEMPLATE, context)
        text_body = render_template(CALCULATION_REPORT_TEXT, context)
        
        # Prepare attachments
        attachments = []
        if pdf_buffer:
            attachments.append({
                'filename': f'{project_name.replace(" ", "_")}_Multi_Site_Report.pdf',
                'content': pdf_buffer,
            })
        
        # Add BCC to sales if configured
        bcc = []
        if self.settings.smtp_bcc:
            bcc.append(self.settings.smtp_bcc)
        
        # Send email
        return await self.send_email(
            to=[recipient_email],
            subject=f'Nx System Calculator Multi-Site Report - {project_name}',
            html_body=html_body,
            text_body=text_body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )

