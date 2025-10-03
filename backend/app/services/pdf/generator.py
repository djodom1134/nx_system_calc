"""PDF report generation using ReportLab."""

from datetime import datetime
from typing import Dict, Any, Optional
from io import BytesIO
import os

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
        Image,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from app.services.pdf.charts import ChartGenerator
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False


class PDFGenerator:
    """Generate PDF reports for VMS calculations."""

    def __init__(self, page_size=None, include_charts=True):
        """Initialize PDF generator."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")

        self.page_size = page_size if page_size is not None else letter
        self.styles = getSampleStyleSheet()
        self.include_charts = include_charts and CHARTS_AVAILABLE
        self.chart_generator = ChartGenerator() if self.include_charts else None
        self.temp_chart_files = []  # Track temporary chart files for cleanup
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles - Network Optix branding."""
        # Title style - Network Optix blue
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#407EC9'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))

        # Section header style - Network Optix blue
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#407EC9'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
        ))

        # Subsection style
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1D252D'),
            spaceAfter=8,
            fontName='Helvetica-Bold',
        ))

    def generate_report(
        self,
        calculation_data: Dict[str, Any],
        output_path: Optional[str] = None,
        company_name: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> BytesIO:
        """
        Generate PDF report from calculation data.

        Args:
            calculation_data: Calculation results dictionary
            output_path: Optional file path to save PDF
            company_name: Optional company name for branding
            logo_path: Optional path to company logo

        Returns:
            BytesIO buffer containing PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build PDF content
        story = []

        # Header
        story.extend(self._build_header(calculation_data, company_name, logo_path))

        # Project Details
        story.extend(self._build_project_details(calculation_data.get('project', {})))

        # Executive Summary
        story.extend(self._build_summary(calculation_data.get('summary', {})))

        # Charts Section (if enabled)
        if self.include_charts:
            story.extend(self._build_charts_section(calculation_data))

        # Detailed Results
        story.extend(self._build_storage_section(calculation_data.get('storage', {})))
        story.extend(self._build_server_section(calculation_data.get('servers', {})))
        story.extend(self._build_bandwidth_section(calculation_data.get('bandwidth', {})))
        story.extend(self._build_license_section(calculation_data.get('licenses', {})))

        # Warnings and Errors
        if calculation_data.get('warnings') or calculation_data.get('errors'):
            story.extend(self._build_warnings_section(
                calculation_data.get('warnings', []),
                calculation_data.get('errors', [])
            ))

        # Footer
        story.extend(self._build_footer())

        # Build PDF
        doc.build(story)

        # Cleanup temporary chart files
        self._cleanup_temp_files()

        if not output_path:
            buffer.seek(0)
            return buffer

        return buffer

    def _cleanup_temp_files(self):
        """Clean up temporary chart files."""
        for file_path in self.temp_chart_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors
        self.temp_chart_files = []

    def _build_header(self, data: Dict, company_name: Optional[str], logo_path: Optional[str]):
        """Build PDF header."""
        elements = []

        # Logo if provided
        if logo_path:
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                elements.append(logo)
                elements.append(Spacer(1, 12))
            except:
                pass

        # Title
        title = company_name or "Network Optix"
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Paragraph("VMS System Calculator Report", self.styles['Heading2']))
        elements.append(Spacer(1, 12))

        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated: {date_str}", self.styles['Normal']))
        elements.append(Spacer(1, 24))

        return elements

    def _build_project_details(self, project: Dict):
        """Build project details section."""
        elements = []
        elements.append(Paragraph("Project Details", self.styles['SectionHeader']))

        data = [
            ["Project Name:", project.get('project_name', 'N/A')],
            ["Created By:", project.get('created_by', 'N/A')],
            ["Email:", project.get('creator_email', 'N/A')],
        ]

        if project.get('description'):
            data.append(["Description:", project.get('description')])

        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_summary(self, summary: Dict):
        """Build executive summary section."""
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        data = [
            ['Metric', 'Value'],
            ['Total Devices', str(summary.get('total_devices', 0))],
            ['Servers Required', str(summary.get('servers_needed', 0))],
            ['Total Storage', f"{summary.get('total_storage_tb', 0):.2f} TB"],
            ['Total Bandwidth', f"{summary.get('total_bitrate_mbps', 0):.2f} Mbps"],
        ]

        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#407EC9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_storage_section(self, storage: Dict):
        """Build storage requirements section."""
        elements = []
        elements.append(Paragraph("Storage Requirements", self.styles['SectionHeader']))

        data = [
            ['Storage Type', 'Capacity'],
            ['Usable Storage', f"{storage.get('total_storage_tb', 0):.2f} TB"],
            ['Raw Storage (with RAID)', f"{storage.get('raw_storage_needed_gb', 0) / 1024:.2f} TB"],
            ['RAID Overhead', f"{storage.get('raid_overhead_gb', 0) / 1024:.2f} TB"],
            ['Daily Storage', f"{storage.get('daily_storage_gb', 0):.2f} GB/day"],
        ]

        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_server_section(self, servers: Dict):
        """Build server configuration section."""
        elements = []
        elements.append(Paragraph("Server Configuration", self.styles['SectionHeader']))

        recommended = servers.get('recommended_tier', {})

        data = [
            ['Configuration', 'Value'],
            ['Servers Required', str(servers.get('servers_needed', 0))],
            ['With Failover', str(servers.get('servers_with_failover', 0))],
            ['Devices per Server', str(servers.get('devices_per_server', 0))],
            ['Bitrate per Server', f"{servers.get('bitrate_per_server_mbps', 0):.2f} Mbps"],
            ['Limiting Factor', servers.get('limiting_factor', 'N/A').replace('_', ' ').title()],
            ['', ''],
            ['Recommended Tier', recommended.get('tier', 'N/A').title()],
            ['CPU', recommended.get('cpu', 'N/A')],
            ['RAM', f"{recommended.get('ram_gb', 0)} GB"],
            ['Storage Type', recommended.get('storage_type', 'N/A')],
        ]

        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_bandwidth_section(self, bandwidth: Dict):
        """Build network bandwidth section."""
        elements = []
        elements.append(Paragraph("Network Bandwidth", self.styles['SectionHeader']))

        data = [
            ['Metric', 'Value'],
            ['Total Bitrate', f"{bandwidth.get('total_bitrate_mbps', 0):.2f} Mbps ({bandwidth.get('total_bitrate_gbps', 0):.2f} Gbps)"],
            ['Per Server', f"{bandwidth.get('per_server_mbps', 0):.2f} Mbps"],
            ['NIC Utilization', f"{bandwidth.get('nic_utilization_percentage', 0):.1f}%"],
        ]

        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_license_section(self, licenses: Dict):
        """Build license requirements section."""
        elements = []
        elements.append(Paragraph("License Requirements", self.styles['SectionHeader']))

        data = [
            ['License Type', 'Quantity'],
            ['Professional Licenses', str(licenses.get('professional_licenses', 0))],
            ['Total Licenses', str(licenses.get('total_licenses', 0))],
            ['Licensing Model', licenses.get('licensing_model', 'N/A').title()],
        ]

        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _build_charts_section(self, calculation_data: Dict[str, Any]):
        """Build charts and visualizations section."""
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Visual Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))

        try:
            # Storage breakdown chart
            storage_data = calculation_data.get('storage', {})
            if storage_data.get('total_storage_gb', 0) > 0:
                chart_path = self.chart_generator.generate_storage_breakdown_chart(storage_data)
                self.temp_chart_files.append(chart_path)

                elements.append(Paragraph("Storage Breakdown", self.styles['Subsection']))
                img = Image(chart_path, width=5*inch, height=3.75*inch)
                elements.append(img)
                elements.append(Spacer(1, 24))

            # Bitrate distribution chart
            camera_groups = calculation_data.get('camera_groups', [])
            if camera_groups:
                chart_path = self.chart_generator.generate_bitrate_distribution_chart(camera_groups)
                self.temp_chart_files.append(chart_path)

                elements.append(Paragraph("Bitrate Distribution", self.styles['Subsection']))
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                elements.append(img)
                elements.append(Spacer(1, 24))

            # Server capacity chart
            server_data = calculation_data.get('servers', {})
            if server_data.get('servers_needed', 0) > 0:
                chart_path = self.chart_generator.generate_server_capacity_chart(server_data)
                self.temp_chart_files.append(chart_path)

                elements.append(Paragraph("Server Capacity Utilization", self.styles['Subsection']))
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                elements.append(img)
                elements.append(Spacer(1, 24))

            # Storage timeline chart
            retention_days = calculation_data.get('retention_days', 30)
            if storage_data.get('daily_storage_gb', 0) > 0:
                chart_path = self.chart_generator.generate_storage_timeline_chart(
                    storage_data, retention_days
                )
                self.temp_chart_files.append(chart_path)

                elements.append(Paragraph("Storage Accumulation Timeline", self.styles['Subsection']))
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                elements.append(img)
                elements.append(Spacer(1, 24))

        except Exception as e:
            # If chart generation fails, add a note but continue
            elements.append(Paragraph(
                f"Note: Chart generation encountered an issue. Continuing with text-based report.",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 12))

        return elements

    def _build_warnings_section(self, warnings: list, errors: list):
        """Build warnings and errors section."""
        elements = []

        if warnings:
            elements.append(Paragraph("Warnings", self.styles['SectionHeader']))
            for warning in warnings:
                elements.append(Paragraph(f"⚠️ {warning}", self.styles['Normal']))
                elements.append(Spacer(1, 6))
            elements.append(Spacer(1, 12))

        if errors:
            elements.append(Paragraph("Errors", self.styles['SectionHeader']))
            for error in errors:
                elements.append(Paragraph(f"❌ {error}", self.styles['Normal']))
                elements.append(Spacer(1, 6))
            elements.append(Spacer(1, 12))

        return elements

    def _build_footer(self):
        """Build PDF footer."""
        elements = []
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(
            "This report was generated by the Nx System Calculator. "
            "All calculations are estimates based on typical usage patterns. "
            "Actual requirements may vary based on specific deployment conditions.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "© 2025 Network Optix, Inc. All rights reserved.",
            self.styles['Normal']
        ))

        return elements

