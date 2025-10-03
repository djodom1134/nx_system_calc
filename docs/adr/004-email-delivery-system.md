# ADR 004: Email Delivery System Design

**Date**: 2025-10-03  
**Status**: ✅ Implemented  
**Decision Makers**: Development Team  
**Related Documents**: `/docs/user-guide/`, Email Implementation Updates

---

## Context

The Nx System Calculator requires the ability to generate PDF reports and deliver them to customers via email. This functionality is critical for sales engineers and system integrators who need to share professional proposals with clients. The system must support:

- Professional HTML email templates
- PDF report attachments
- Automatic BCC to sales team
- OEM branding customization
- Reliable delivery with error handling
- SMTP configuration flexibility

---

## Decision

We will implement an email delivery system with the following architecture:

### Core Components

1. **SMTP Integration**
   - Use Python's `smtplib` with TLS encryption
   - Support multiple SMTP providers (Gmail, Office 365, SendGrid, etc.)
   - Configurable via environment variables
   - Connection pooling for performance

2. **Email Templates**
   - HTML templates with inline CSS for compatibility
   - Responsive design for mobile email clients
   - OEM branding support (logo, colors, company name)
   - Plain text fallback for accessibility

3. **PDF Attachment**
   - Generate PDF using ReportLab
   - Attach to email as `application/pdf`
   - Filename format: `NX_System_Calculation_[ProjectName]_[Date].pdf`

4. **Delivery Features**
   - Automatic BCC to sales team email
   - Delivery confirmation logging
   - Error handling with retry logic
   - Rate limiting to prevent spam flags

---

## Implementation Details

### Email Service Architecture

```python
# app/services/email/email_service.py

class EmailService:
    def __init__(self, smtp_config: SMTPConfig):
        self.smtp_host = smtp_config.host
        self.smtp_port = smtp_config.port
        self.smtp_user = smtp_config.user
        self.smtp_password = smtp_config.password
        self.from_address = smtp_config.from_address
        self.bcc_address = smtp_config.bcc_address
    
    async def send_report(
        self,
        recipient_email: str,
        recipient_name: str,
        pdf_path: str,
        project_name: str,
        branding: Optional[BrandingConfig] = None
    ) -> EmailDeliveryResult:
        """Send calculation report via email."""
        
        # Generate HTML email from template
        html_content = self._render_template(
            recipient_name=recipient_name,
            project_name=project_name,
            branding=branding
        )
        
        # Create multipart message
        message = MIMEMultipart('alternative')
        message['Subject'] = f"Nx System Calculation: {project_name}"
        message['From'] = self.from_address
        message['To'] = recipient_email
        message['Bcc'] = self.bcc_address
        
        # Attach HTML and plain text
        message.attach(MIMEText(self._generate_plain_text(), 'plain'))
        message.attach(MIMEText(html_content, 'html'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=os.path.basename(pdf_path)
            )
            message.attach(pdf_attachment)
        
        # Send email
        return await self._send_smtp(message, recipient_email)
```

### Email Template Design

**HTML Template Features:**
- Professional Network Optix branding
- Clear call-to-action
- Project summary highlights
- Contact information
- Legal disclaimers
- Mobile-responsive design

**Template Variables:**
- `{{recipient_name}}`: Personalization
- `{{project_name}}`: Project identifier
- `{{company_logo}}`: OEM logo URL
- `{{company_name}}`: OEM company name
- `{{primary_color}}`: Brand color
- `{{contact_email}}`: Support email

### SMTP Configuration

**Supported Providers:**

1. **Gmail**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=app-password  # Use App Password
   ```

2. **Office 365**
   ```bash
   SMTP_HOST=smtp.office365.com
   SMTP_PORT=587
   SMTP_USER=your-email@company.com
   SMTP_PASSWORD=your-password
   ```

3. **SendGrid**
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   ```

---

## Rationale

### Why SMTP over API-based services?

**Advantages:**
- ✅ Universal compatibility with any email provider
- ✅ No vendor lock-in
- ✅ Lower cost (use existing email infrastructure)
- ✅ Simpler configuration
- ✅ Better for on-premise deployments

**Disadvantages:**
- ❌ Less detailed delivery analytics
- ❌ No built-in template management
- ❌ Manual retry logic required

**Decision**: SMTP provides the best balance of flexibility, cost, and compatibility for our use case.

### Why HTML emails with inline CSS?

- Maximum compatibility across email clients
- Professional appearance
- Branding consistency
- Mobile responsiveness

### Why automatic BCC to sales?

- Sales team visibility into customer interactions
- Lead tracking and follow-up
- Quality assurance
- Compliance and record-keeping

---

## Alternatives Considered

### Alternative 1: SendGrid API

**Pros:**
- Rich analytics and tracking
- Template management UI
- Better deliverability
- Webhook support for events

**Cons:**
- Vendor lock-in
- Additional cost
- API complexity
- Requires internet connectivity

**Rejected**: Too complex for initial implementation, can be added later.

### Alternative 2: AWS SES

**Pros:**
- Low cost at scale
- High deliverability
- AWS ecosystem integration
- Detailed metrics

**Cons:**
- AWS account required
- More complex setup
- Region-specific
- Sandbox mode restrictions

**Rejected**: Adds AWS dependency, SMTP is more flexible.

### Alternative 3: In-app download only (no email)

**Pros:**
- Simplest implementation
- No email configuration needed
- No delivery failures

**Cons:**
- Poor user experience
- Manual sharing required
- No sales team visibility
- Unprofessional

**Rejected**: Email delivery is a core requirement.

---

## Risk Mitigation

### Risk 1: Email Delivery Failures

**Mitigation:**
- Comprehensive error handling and logging
- Retry logic with exponential backoff
- Fallback to download link if email fails
- User notification of delivery status

### Risk 2: Spam Filtering

**Mitigation:**
- SPF/DKIM/DMARC configuration documentation
- Professional email content
- Rate limiting
- Avoid spam trigger words
- Plain text alternative

### Risk 3: SMTP Credential Security

**Mitigation:**
- Environment variables for credentials
- Never commit credentials to git
- Support for app-specific passwords
- Encrypted storage in production

### Risk 4: Large Attachments

**Mitigation:**
- PDF optimization (compress images)
- Size limit warnings
- Alternative cloud storage for large files
- Typical PDF size: 200-500 KB (well within limits)

---

## Implementation Checklist

- [x] SMTP service implementation
- [x] HTML email template design
- [x] PDF attachment handling
- [x] BCC functionality
- [x] Error handling and logging
- [x] Configuration via environment variables
- [x] OEM branding support
- [x] Plain text fallback
- [x] Delivery confirmation
- [x] Unit tests for email service
- [x] Integration tests
- [x] Documentation

---

## Success Metrics

**Technical Metrics:**
- Email delivery success rate > 99%
- Average delivery time < 5 seconds
- Zero credential leaks
- Error rate < 1%

**Business Metrics:**
- Sales team BCC delivery rate 100%
- Customer satisfaction with email format
- Reduction in manual report sharing

---

## Future Enhancements

1. **Email Analytics**
   - Open tracking
   - Click tracking
   - Delivery confirmation webhooks

2. **Template Management**
   - Admin UI for template editing
   - A/B testing for email content
   - Multi-language support

3. **Advanced Features**
   - Scheduled email delivery
   - Email campaigns for multiple recipients
   - Integration with CRM systems

4. **Alternative Delivery**
   - Cloud storage links (S3, Azure Blob)
   - Webhook notifications
   - API-based delivery for integrations

---

## References

- [RFC 5321 - SMTP](https://tools.ietf.org/html/rfc5321)
- [Email Template Best Practices](https://www.campaignmonitor.com/dev-resources/)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [MIME Types](https://www.iana.org/assignments/media-types/media-types.xhtml)

---

## Approval

**Approved by**: Development Team  
**Implementation Date**: 2025-10-03  
**Review Date**: 2026-01-03 (Quarterly review)

