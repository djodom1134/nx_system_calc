# Nx System Calculator - Documentation

**Complete documentation for the Nx System Calculator**

---

## 📚 Documentation Index

### Getting Started

- **[Main README](../README.md)** - Project overview and quick start
- **[User Manual](user-guide/README.md)** - Complete user guide
- **[Configuration Guide](configuration-guide.md)** - System configuration
- **[Deployment Guide](deployment-guide.md)** - Production deployment

### API Documentation

- **[API Reference](api/README.md)** - Complete API documentation
- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI (when running)
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API docs (when running)

### Architecture & Design

- **[ADR 001: Technology Stack Selection](adr/001-technology-stack-selection.md)**
- **[ADR 002: Calculation Engine Design](adr/002-calculation-engine-design.md)**
- **[ADR 003: Calculation Formula Alignment](adr/003-calculation-formula-alignment.md)**
- **[ADR 004: Email Delivery System](adr/004-email-delivery-system.md)**
- **[ADR 005: OEM White-Labeling](adr/005-oem-white-labeling.md)**

### Technical Documentation

- **[Core Calculations](core_calculations.md)** - Mathematical formulas and algorithms
- **[Observability Guide](observability-guide.md)** - Logging, metrics, and monitoring
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute

### Project Updates

- **[Implementation Status](updates/IMPLEMENTATION_STATUS.md)**
- **[Final Status Report](updates/FINAL_STATUS_REPORT.md)**
- **[Project Summary](updates/PROJECT_SUMMARY.md)**

---

## 🎯 Quick Links by Role

### For End Users

1. **[User Manual](user-guide/README.md)** - How to use the calculator
2. **[FAQ](user-guide/README.md#faq)** - Frequently asked questions
3. **[Troubleshooting](user-guide/README.md#troubleshooting)** - Common issues

### For Developers

1. **[Contributing Guide](../CONTRIBUTING.md)** - Development workflow
2. **[API Documentation](api/README.md)** - API reference
3. **[Architecture Decisions](adr/)** - Design decisions and rationale
4. **[Core Calculations](core_calculations.md)** - Calculation algorithms

### For DevOps/SRE

1. **[Deployment Guide](deployment-guide.md)** - Production deployment
2. **[Configuration Guide](configuration-guide.md)** - System configuration
3. **[Observability Guide](observability-guide.md)** - Monitoring and logging

### For System Integrators

1. **[User Manual](user-guide/README.md)** - Complete usage guide
2. **[Configuration Guide](configuration-guide.md)** - Customization options
3. **[API Documentation](api/README.md)** - Integration reference

---

## 📖 Documentation Structure

```
docs/
├── README.md                          # This file - documentation index
├── core_calculations.md               # Mathematical formulas
├── configuration-guide.md             # Configuration reference
├── deployment-guide.md                # Deployment instructions
├── observability-guide.md             # Monitoring and logging
│
├── adr/                               # Architecture Decision Records
│   ├── 001-technology-stack-selection.md
│   ├── 002-calculation-engine-design.md
│   ├── 003-calculation-formula-alignment.md
│   ├── 004-email-delivery-system.md
│   └── 005-oem-white-labeling.md
│
├── api/                               # API Documentation
│   └── README.md                      # API reference guide
│
├── user-guide/                        # User Manual
│   └── README.md                      # Complete user guide
│
├── screenshots/                       # Application screenshots
│   ├── calculator-interface.png
│   ├── results-panel.png
│   ├── pdf-report-sample.png
│   └── branding-settings.png
│
└── updates/                           # Project status updates
    ├── IMPLEMENTATION_STATUS.md
    ├── FINAL_STATUS_REPORT.md
    └── PROJECT_SUMMARY.md
```

---

## 🚀 Common Tasks

### Running the Application

```bash
# Development mode
./run.sh dev

# Production with Docker
docker-compose up -d
```

See: [Deployment Guide](deployment-guide.md)

### Making a Calculation

1. Open the calculator interface
2. Enter project information
3. Configure camera groups
4. Set retention period
5. Configure server settings
6. Review results

See: [User Manual](user-guide/README.md#using-the-calculator)

### Generating a Report

1. Complete your calculation
2. Click "Generate PDF Report"
3. Or click "Email Report" to send via email

See: [User Manual](user-guide/README.md#generating-reports)

### Customizing Branding

1. Navigate to Branding Settings
2. Upload your company logo
3. Set brand colors
4. Enter company information
5. Save configuration

See: [User Manual](user-guide/README.md#customization--branding)

### Integrating via API

```bash
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d @calculation-request.json
```

See: [API Documentation](api/README.md)

---

## 🔧 Configuration

### Environment Variables

Key configuration options:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com
```

See: [Configuration Guide](configuration-guide.md)

### Customizing Presets

Edit JSON configuration files:

- `config/resolutions.json` - Camera resolutions
- `config/codecs.json` - Video codecs
- `config/raid_types.json` - RAID configurations
- `config/server_specs.json` - Server specifications

See: [Configuration Guide](configuration-guide.md#customizing-presets)

---

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

See: [Contributing Guide](../CONTRIBUTING.md#testing-requirements)

### Test Coverage Requirements

- Backend: ≥ 85% coverage
- Frontend: ≥ 80% coverage
- Mutation score: ≥ 70%

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Logs

```bash
# Docker logs
docker-compose logs -f backend

# Application logs
tail -f backend/logs/app.log
```

See: [Observability Guide](observability-guide.md)

---

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Check environment variables
- Verify database connection
- Review logs for errors

**Calculation errors:**
- Validate input parameters
- Check configuration files
- Review calculation logs

**Email delivery fails:**
- Verify SMTP credentials
- Check firewall rules
- Test SMTP connection

See: [User Manual - Troubleshooting](user-guide/README.md#troubleshooting)

---

## 📞 Support

### Getting Help

- **Email**: support@networkoptix.com
- **Documentation**: https://docs.networkoptix.com
- **GitHub Issues**: https://github.com/networkoptix/nx_system_calc/issues
- **Community Forum**: https://community.networkoptix.com

### Reporting Issues

1. Check existing issues
2. Gather relevant information (logs, screenshots)
3. Create detailed issue report
4. Include steps to reproduce

See: [Contributing Guide](../CONTRIBUTING.md#issue-reporting)

---

## 📝 Contributing

We welcome contributions! Please read:

1. **[Contributing Guide](../CONTRIBUTING.md)** - Development workflow
2. **[Code of Conduct](../CONTRIBUTING.md#code-of-conduct)** - Community guidelines
3. **[Coding Standards](../CONTRIBUTING.md#coding-standards)** - Style guide

---

## 📄 License

Copyright © 2025 Network Optix, Inc. All rights reserved.

See [LICENSE](../LICENSE) for details.

---

## 🔄 Documentation Updates

This documentation is actively maintained. Last updated: **October 2025**

To suggest improvements:
1. Open an issue on GitHub
2. Submit a pull request
3. Contact the documentation team

---

## 📚 Additional Resources

### External Documentation

- **Network Optix Website**: https://www.networkoptix.com
- **VMS Documentation**: https://docs.networkoptix.com
- **Community Forum**: https://community.networkoptix.com
- **YouTube Channel**: https://youtube.com/networkoptix

### Related Projects

- **Nx Witness VMS**: https://www.networkoptix.com/nx-witness
- **Nx Meta**: https://www.networkoptix.com/nx-meta
- **Developer Portal**: https://developer.networkoptix.com

### Learning Resources

- **VMS Best Practices**: https://www.networkoptix.com/best-practices
- **System Design Guide**: https://www.networkoptix.com/system-design
- **Training Videos**: https://www.networkoptix.com/training

---

**Need help? Contact us at support@networkoptix.com**

