# Email Delivery System Implementation

## Overview

The Nx System Calculator now includes a comprehensive email delivery system that allows users to receive calculation reports via email with optional PDF attachments. The system is built using `aiosmtplib` for asynchronous SMTP communication and `Jinja2` for HTML email templates.

## Features

✅ **Professional HTML Email Templates**
- Responsive design with modern styling
- Project summary with key metrics
- Warning/error display
- Branded footer with Network Optix branding

✅ **PDF Attachment Support**
- Automatic PDF generation from calculation results
- Configurable attachment inclusion
- Support for large attachments (tested up to 5MB)

✅ **Flexible Recipient Management**
- Primary recipient (TO)
- CC recipients (optional)
- Automatic BCC to sales team (configurable)

✅ **Email Validation**
- Pydantic EmailStr validation
- Proper email address format checking

✅ **Asynchronous Delivery**
- Non-blocking email sending using background tasks
- Fast API response times

✅ **Error Handling**
- Graceful failure handling
- Detailed error messages
- SMTP connection validation

## Architecture

### Components

1. **Email Service** (`backend/app/services/email/sender.py`)
   - Core email sending functionality
   - SMTP connection management
   - Attachment handling
   - Template rendering integration

2. **Email Templates** (`backend/app/services/email/templates.py`)
   - HTML email templates
   - Plain text fallback templates
   - Jinja2 template rendering

3. **Email API** (`backend/app/api/email.py`)
   - REST API endpoints
   - Request/response models
   - Integration with calculation engine

4. **Configuration** (`backend/app/core/config.py`)
   - SMTP server settings
   - Email credentials
   - Default sender/BCC addresses

## Configuration

### Environment Variables

Set the following environment variables to configure the email system:

```bash
# SMTP Server Configuration
SMTP_HOST=smtp.gmail.com          # SMTP server hostname
SMTP_PORT=587                      # SMTP server port (587 for TLS)
SMTP_USER=your-email@example.com  # SMTP username
SMTP_PASSWORD=your-password        # SMTP password

# Email Addresses
SMTP_FROM=noreply@networkoptix.com      # Default sender address
SMTP_BCC=sales@networkoptix.com         # Default BCC address (optional)
```

### Gmail Configuration Example

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password as `SMTP_PASSWORD`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Office 365 Configuration Example

```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-password
```

## API Endpoints

### 1. Send Test Email

**Endpoint:** `POST /api/v1/email/test`

**Purpose:** Verify SMTP configuration by sending a test email.

**Request:**
```json
{
  "recipient_email": "test@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully to 1 recipient(s)",
  "recipients": ["test@example.com"]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/email/test" \
  -H "Content-Type: application/json" \
  -d '{"recipient_email": "test@example.com"}'
```

### 2. Send Calculation Report

**Endpoint:** `POST /api/v1/email/send-report`

**Purpose:** Calculate system requirements and send results via email with optional PDF attachment.

**Request:**
```json
{
  "calculation": {
    "project": {
      "project_name": "Enterprise Deployment",
      "created_by": "John Doe",
      "creator_email": "john@example.com"
    },
    "camera_groups": [
      {
        "num_cameras": 100,
        "resolution_id": "4mp",
        "fps": 30,
        "codec_id": "h264",
        "quality": "medium",
        "recording_mode": "continuous",
        "audio_enabled": false,
        "bitrate_kbps": 4000
      }
    ],
    "retention_days": 30,
    "server_config": {
      "raid_type": "raid5",
      "failover_type": "none",
      "nic_capacity_mbps": 1000,
      "nic_count": 1
    }
  },
  "email": {
    "recipient_email": "customer@example.com",
    "recipient_name": "Jane Smith",
    "cc": ["manager@example.com"],
    "include_pdf": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email will be sent to customer@example.com",
  "recipients": ["customer@example.com"]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/email/send-report" \
  -H "Content-Type: application/json" \
  -d @calculation_request.json
```

## Email Templates

### Calculation Report Template

The calculation report email includes:

- **Header:** Branded header with Nx System Calculator logo
- **Greeting:** Personalized greeting with recipient name
- **Project Summary:** Key metrics in a formatted table
  - Total Cameras
  - Servers Required
  - Total Storage (TB)
  - Total Bandwidth (Mbps)
  - Retention Period (days)
- **Warnings:** Highlighted warnings section (if any)
- **PDF Attachment:** Link to attached PDF report
- **Footer:** Network Optix branding and copyright

### Template Customization

To customize email templates, edit `backend/app/services/email/templates.py`:

```python
CALCULATION_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <!-- Your custom styles -->
</head>
<body>
    <!-- Your custom template -->
</body>
</html>
"""
```

## Usage Examples

### Python SDK Example

```python
import httpx
import asyncio

async def send_calculation_email():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/email/send-report",
            json={
                "calculation": {
                    # ... calculation data ...
                },
                "email": {
                    "recipient_email": "customer@example.com",
                    "recipient_name": "Jane Smith",
                    "include_pdf": True
                }
            }
        )
        print(response.json())

asyncio.run(send_calculation_email())
```

### JavaScript/TypeScript Example

```typescript
const response = await fetch('http://localhost:8000/api/v1/email/send-report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    calculation: {
      // ... calculation data ...
    },
    email: {
      recipient_email: 'customer@example.com',
      recipient_name: 'Jane Smith',
      include_pdf: true,
    },
  }),
});

const result = await response.json();
console.log(result);
```

## Testing

### Running Tests

```bash
# Run all email tests
cd backend
python3 -m pytest app/tests/test_email.py app/tests/test_email_api.py -v

# Run specific test
python3 -m pytest app/tests/test_email.py::TestEmailService::test_send_email_success -v
```

### Test Coverage

- **14 Unit Tests** (`test_email.py`)
  - Email template rendering
  - Email service functionality
  - Attachment handling
  - Error handling
  - Edge cases

- **16 Integration Tests** (`test_email_api.py`)
  - API endpoint testing
  - Request validation
  - Calculation integration
  - Documentation verification

**Total: 30 Tests - All Passing ✅**

## Security Considerations

1. **Credentials Storage**
   - Never commit SMTP credentials to version control
   - Use environment variables or secure secret management
   - Rotate passwords regularly

2. **Email Validation**
   - All email addresses are validated using Pydantic EmailStr
   - Invalid emails are rejected with 422 status code

3. **Rate Limiting**
   - Consider implementing rate limiting for production
   - Prevent email spam/abuse

4. **TLS/SSL**
   - Always use TLS (port 587) or SSL (port 465)
   - Never send credentials over unencrypted connections

## Troubleshooting

### Common Issues

**1. "SMTP credentials not configured"**
- **Cause:** SMTP_USER or SMTP_PASSWORD not set
- **Solution:** Set environment variables with valid credentials

**2. "Connection timeout"**
- **Cause:** Firewall blocking SMTP port or incorrect hostname
- **Solution:** Verify SMTP_HOST and SMTP_PORT, check firewall rules

**3. "Authentication failed"**
- **Cause:** Invalid credentials or 2FA not configured
- **Solution:** Verify credentials, use App Password for Gmail

**4. "Email not received"**
- **Cause:** Email in spam folder or incorrect recipient
- **Solution:** Check spam folder, verify recipient email address

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Email delivery tracking and status
- [ ] Email templates customization UI
- [ ] Support for multiple email providers
- [ ] Email queue with retry logic
- [ ] Email analytics and reporting
- [ ] Unsubscribe functionality
- [ ] Email preview before sending

## Dependencies

- `aiosmtplib==3.0.1` - Async SMTP client
- `jinja2==3.1.3` - Template engine
- `email-validator==2.1.0` - Email validation
- `pydantic[email]` - Email validation support

## License

Copyright © 2025 Network Optix. All rights reserved.

