"""Email templates for Nx System Calculator."""

from typing import Dict, Any


# HTML email template for calculation report with OEM branding support
CALCULATION_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }
        .email-container {
            background-color: #ffffff;
            margin: 20px auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, {{ primary_color|default('#2563eb') }} 0%, {{ secondary_color|default('#3b82f6') }} 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            border-radius: 0;
        }
        .logo {
            max-width: 200px;
            max-height: 80px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.95;
        }
        .content {
            background: #ffffff;
            padding: 40px 30px;
        }
        .greeting {
            font-size: 18px;
            color: #111827;
            margin-bottom: 20px;
        }
        .summary-box {
            background: #f9fafb;
            border-left: 4px solid {{ accent_color|default('#2563eb') }};
            padding: 24px;
            margin: 24px 0;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .summary-box h2 {
            margin-top: 0;
            margin-bottom: 20px;
            color: {{ accent_color|default('#2563eb') }};
            font-size: 20px;
            font-weight: 600;
        }
        .summary-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        .summary-item:last-child {
            border-bottom: none;
        }
        .summary-label {
            font-weight: 600;
            color: #6b7280;
            font-size: 15px;
        }
        .summary-value {
            color: #111827;
            font-weight: 700;
            font-size: 15px;
        }
        .warning-box {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            margin: 20px 0;
            border-radius: 6px;
        }
        .warning-box h2 {
            margin-top: 0;
            color: #d97706;
            font-size: 18px;
        }
        .warning-box ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .warning-box li {
            color: #92400e;
            margin: 8px 0;
        }
        .cta-button {
            display: inline-block;
            background: {{ accent_color|default('#2563eb') }};
            color: white !important;
            padding: 14px 28px;
            text-decoration: none;
            border-radius: 8px;
            margin: 24px 0;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .cta-button:hover {
            background: {{ primary_color|default('#1e40af') }};
        }
        .footer {
            background: #f9fafb;
            text-align: center;
            padding: 30px 20px;
            color: #6b7280;
            font-size: 14px;
            border-top: 1px solid #e5e7eb;
        }
        .footer a {
            color: {{ accent_color|default('#2563eb') }};
            text-decoration: none;
            font-weight: 500;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .divider {
            height: 1px;
            background: #e5e7eb;
            margin: 30px 0;
        }
        @media only screen and (max-width: 600px) {
            .content {
                padding: 30px 20px;
            }
            .header {
                padding: 30px 20px;
            }
            .summary-item {
                flex-direction: column;
                gap: 4px;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ company_name|default('Network Optix') }}" class="logo">
            {% endif %}
            <h1>🎥 {{ company_name|default('Nx System Calculator') }} Report</h1>
            <p>Your VMS system requirements are ready</p>
        </div>

        <div class="content">
            <p class="greeting">Hello {{ recipient_name }},</p>

            <p>Thank you for using the {{ company_name|default('Nx System Calculator') }}. Your system requirements calculation for <strong>{{ project_name }}</strong> is complete.</p>

            <div class="summary-box">
                <h2>📊 System Summary</h2>
                <div class="summary-item">
                    <span class="summary-label">Total Cameras:</span>
                    <span class="summary-value">{{ total_devices }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Servers Required:</span>
                    <span class="summary-value">{{ servers_needed }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Total Storage:</span>
                    <span class="summary-value">{{ total_storage_tb }} TB</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Total Bandwidth:</span>
                    <span class="summary-value">{{ total_bitrate_mbps }} Mbps</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Retention Period:</span>
                    <span class="summary-value">{{ retention_days }} days</span>
                </div>
            </div>

            <p>📎 A detailed PDF report is attached to this email with complete specifications, recommendations, and technical details.</p>

            {% if warnings %}
            <div class="warning-box">
                <h2>⚠️ Important Warnings</h2>
                <ul>
                {% for warning in warnings %}
                    <li>{{ warning }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}

            <div class="divider"></div>

            <p>If you have any questions or need assistance with your deployment, please don't hesitate to contact us.</p>

            <p>Best regards,<br>
            <strong>{{ company_name|default('Network Optix') }} Team</strong></p>
        </div>

        <div class="footer">
            <p>This email was generated by the <a href="{{ website|default('https://networkoptix.com') }}">{{ company_name|default('Nx System Calculator') }}</a></p>
            {% if tagline %}
            <p style="font-style: italic; color: #9ca3af;">{{ tagline }}</p>
            {% endif %}
            <p>© {{ year }} {{ company_name|default('Network Optix') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


# Plain text version for email clients that don't support HTML
CALCULATION_REPORT_TEXT = """
Nx System Calculator Report
===========================

Hello {{ recipient_name }},

Thank you for using the Nx System Calculator. Your system requirements calculation for "{{ project_name }}" is complete.

SYSTEM SUMMARY
--------------
Total Cameras:     {{ total_devices }}
Servers Required:  {{ servers_needed }}
Total Storage:     {{ total_storage_tb }} TB
Total Bandwidth:   {{ total_bitrate_mbps }} Mbps
Retention Period:  {{ retention_days }} days

A detailed PDF report is attached to this email with complete specifications, recommendations, and technical details.

{% if warnings %}
WARNINGS
--------
{% for warning in warnings %}
- {{ warning }}
{% endfor %}
{% endif %}

If you have any questions or need assistance with your deployment, please don't hesitate to contact us.

Best regards,
Network Optix Team

---
This email was generated by the Nx System Calculator
© {{ year }} Network Optix. All rights reserved.
"""


# Test email template
TEST_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: #2563eb;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
        }
        .content {
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Email Configuration Test</h1>
    </div>
    <div class="content">
        <p>This is a test email from the Nx System Calculator.</p>
        <p>If you're reading this, your email configuration is working correctly!</p>
        <p><strong>Timestamp:</strong> {{ timestamp }}</p>
    </div>
</body>
</html>
"""


TEST_EMAIL_TEXT = """
Email Configuration Test
========================

This is a test email from the Nx System Calculator.

If you're reading this, your email configuration is working correctly!

Timestamp: {{ timestamp }}
"""


def render_template(template: str, context: Dict[str, Any]) -> str:
    """
    Render email template with context using Jinja2.

    Args:
        template: Template string with Jinja2 syntax
        context: Dictionary of variables to render in template

    Returns:
        Rendered template string
    """
    from jinja2 import Template
    return Template(template).render(**context)


# Welcome email template
WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }
        .email-container {
            background-color: #ffffff;
            margin: 20px auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, {{ primary_color|default('#2563eb') }} 0%, {{ secondary_color|default('#3b82f6') }} 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .logo {
            max-width: 200px;
            max-height: 80px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .content {
            padding: 40px 30px;
        }
        .feature-box {
            background: #f9fafb;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid {{ accent_color|default('#2563eb') }};
        }
        .feature-box h3 {
            margin-top: 0;
            color: {{ accent_color|default('#2563eb') }};
        }
        .cta-button {
            display: inline-block;
            background: {{ accent_color|default('#2563eb') }};
            color: white !important;
            padding: 14px 28px;
            text-decoration: none;
            border-radius: 8px;
            margin: 24px 0;
            font-weight: 600;
        }
        .footer {
            background: #f9fafb;
            text-align: center;
            padding: 30px 20px;
            color: #6b7280;
            font-size: 14px;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ company_name|default('Network Optix') }}" class="logo">
            {% endif %}
            <h1>Welcome to {{ company_name|default('Nx System Calculator') }}! 🎉</h1>
        </div>

        <div class="content">
            <p>Hello {{ recipient_name }},</p>

            <p>Thank you for choosing the {{ company_name|default('Nx System Calculator') }}. We're excited to help you design your VMS deployment!</p>

            <div class="feature-box">
                <h3>🎯 What You Can Do:</h3>
                <ul>
                    <li>Calculate exact server requirements for your camera deployment</li>
                    <li>Estimate storage needs based on retention policies</li>
                    <li>Optimize bandwidth and network configuration</li>
                    <li>Generate professional PDF reports</li>
                    <li>Share results via email</li>
                </ul>
            </div>

            <p style="text-align: center;">
                <a href="{{ calculator_url|default('https://calculator.networkoptix.com') }}" class="cta-button">
                    Start Calculating →
                </a>
            </p>

            <p>If you have any questions, our support team is here to help!</p>

            <p>Best regards,<br>
            <strong>{{ company_name|default('Network Optix') }} Team</strong></p>
        </div>

        <div class="footer">
            <p>© {{ year }} {{ company_name|default('Network Optix') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


# Error notification email template
ERROR_NOTIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }
        .email-container {
            background-color: #ffffff;
            margin: 20px auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .content {
            padding: 40px 30px;
        }
        .error-box {
            background: #fee2e2;
            border-left: 4px solid #dc2626;
            padding: 20px;
            margin: 20px 0;
            border-radius: 6px;
        }
        .error-box h3 {
            margin-top: 0;
            color: #dc2626;
        }
        .error-details {
            background: #f9fafb;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
            overflow-x: auto;
        }
        .footer {
            background: #f9fafb;
            text-align: center;
            padding: 30px 20px;
            color: #6b7280;
            font-size: 14px;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>⚠️ Calculation Error</h1>
        </div>

        <div class="content">
            <p>Hello {{ recipient_name }},</p>

            <p>We encountered an error while processing your calculation request for <strong>{{ project_name }}</strong>.</p>

            <div class="error-box">
                <h3>Error Details:</h3>
                <div class="error-details">{{ error_message }}</div>
            </div>

            <p><strong>What to do next:</strong></p>
            <ul>
                <li>Check your input parameters and try again</li>
                <li>Contact support if the problem persists</li>
                <li>Include the error details above when contacting support</li>
            </ul>

            <p>We apologize for the inconvenience.</p>

            <p>Best regards,<br>
            <strong>{{ company_name|default('Network Optix') }} Team</strong></p>
        </div>

        <div class="footer">
            <p>© {{ year }} {{ company_name|default('Network Optix') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


# Multi-site calculation report template
MULTI_SITE_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }
        .email-container {
            background-color: #ffffff;
            margin: 20px auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, {{ primary_color|default('#2563eb') }} 0%, {{ secondary_color|default('#3b82f6') }} 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .logo {
            max-width: 200px;
            max-height: 80px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .content {
            padding: 40px 30px;
        }
        .summary-box {
            background: #f9fafb;
            border-left: 4px solid {{ accent_color|default('#2563eb') }};
            padding: 24px;
            margin: 24px 0;
            border-radius: 6px;
        }
        .summary-box h2 {
            margin-top: 0;
            color: {{ accent_color|default('#2563eb') }};
            font-size: 20px;
        }
        .site-card {
            background: white;
            border: 1px solid #e5e7eb;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
        }
        .site-card h3 {
            margin-top: 0;
            color: #111827;
            font-size: 18px;
        }
        .site-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .stat-item {
            padding: 10px;
            background: #f9fafb;
            border-radius: 4px;
        }
        .stat-label {
            font-size: 12px;
            color: #6b7280;
            font-weight: 600;
        }
        .stat-value {
            font-size: 18px;
            color: #111827;
            font-weight: 700;
        }
        .footer {
            background: #f9fafb;
            text-align: center;
            padding: 30px 20px;
            color: #6b7280;
            font-size: 14px;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ company_name|default('Network Optix') }}" class="logo">
            {% endif %}
            <h1>🏢 Multi-Site Deployment Report</h1>
            <p>{{ project_name }}</p>
        </div>

        <div class="content">
            <p>Hello {{ recipient_name }},</p>

            <p>Your multi-site VMS deployment calculation is complete. Here's a summary of your {{ site_count }} site(s):</p>

            <div class="summary-box">
                <h2>📊 Overall Summary</h2>
                <div class="site-stats">
                    <div class="stat-item">
                        <div class="stat-label">Total Sites</div>
                        <div class="stat-value">{{ site_count }}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Cameras</div>
                        <div class="stat-value">{{ total_cameras }}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Servers</div>
                        <div class="stat-value">{{ total_servers }}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Storage</div>
                        <div class="stat-value">{{ total_storage_tb }} TB</div>
                    </div>
                </div>
            </div>

            {% for site in sites %}
            <div class="site-card">
                <h3>📍 {{ site.name }}</h3>
                <div class="site-stats">
                    <div class="stat-item">
                        <div class="stat-label">Cameras</div>
                        <div class="stat-value">{{ site.cameras }}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Servers</div>
                        <div class="stat-value">{{ site.servers }}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Storage</div>
                        <div class="stat-value">{{ site.storage_tb }} TB</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Bandwidth</div>
                        <div class="stat-value">{{ site.bandwidth_mbps }} Mbps</div>
                    </div>
                </div>
            </div>
            {% endfor %}

            <p>📎 A detailed PDF report with complete specifications for all sites is attached.</p>

            <p>Best regards,<br>
            <strong>{{ company_name|default('Network Optix') }} Team</strong></p>
        </div>

        <div class="footer">
            <p>© {{ year }} {{ company_name|default('Network Optix') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

