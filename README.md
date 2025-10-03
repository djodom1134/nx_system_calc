# Nx System Calculator

A modern web-based VMS (Video Management System) calculator for estimating hardware and storage requirements for Network Optix deployments.

## 🎯 Purpose

The Nx System Calculator helps sales engineers, system integrators, and customers quickly determine:
- Required server count and specifications
- Total storage capacity needed
- Network bandwidth requirements
- License counts
- Per-server load distribution

## ✨ Features

- **Real-time Calculations**: Instant results as you input parameters
- **Multi-Site Support**: Handle deployments across multiple sites (max 2560 devices per site)
- **Professional Reports**: Generate branded PDF reports with charts and recommendations
- **OEM White-Labeling**: Customize with your own logo and branding
- **Email Delivery**: Send reports directly to customers with automatic BCC to sales
- **API Access**: RESTful API for integration with other systems
- **Accessibility**: WCAG 2.1 AA compliant interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.11+ (optimized for Apple Silicon)
- FastAPI for REST API
- SQLite (development) / PostgreSQL (production)
- ReportLab for PDF generation
- Pydantic for data validation

**Frontend:**
- React 18 with TypeScript
- Vite for fast builds
- Zustand for state management
- Tailwind CSS for styling

**Testing:**
- Pytest (backend) - Target: ≥85% coverage
- Vitest + Testing Library (frontend)
- Mutation testing (≥70% score)

### Project Structure

```
nx_system_calc/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   │   ├── calculations/  # Calculation engine
│   │   │   ├── pdf/           # PDF generation
│   │   │   └── email/         # Email delivery
│   │   ├── schemas/           # Pydantic schemas
│   │   └── tests/             # Backend tests
│   ├── config/                # Configuration files
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── stores/            # Zustand stores
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Frontend tests
│   └── package.json           # Node dependencies
│
├── config/                     # Shared configuration
│   ├── resolutions.json       # Camera resolution presets
│   ├── codecs.json            # Codec parameters
│   ├── raid_types.json        # RAID configurations
│   └── server_specs.json      # Server specifications
│
├── docs/                       # Documentation
│   ├── adr/                   # Architecture Decision Records
│   ├── api/                   # API documentation
│   └── user-guide/            # User manual
│
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 20 LTS or higher
- Git

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd nx_system_calc
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend setup:**
```bash
cd frontend
npm install
```

4. **Configuration:**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Development

**Start backend server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Start frontend dev server:**
```bash
cd frontend
npm run dev
```

Access the application at `http://localhost:5173`

API documentation available at `http://localhost:8000/docs`

### Docker Deployment

```bash
docker-compose up -d
```

### Quick API Test

```bash
# Test the calculation endpoint
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "project": {
      "project_name": "Test Project",
      "created_by": "John Doe",
      "creator_email": "john@example.com"
    },
    "camera_groups": [{
      "num_cameras": 100,
      "resolution_id": "2mp_1080p",
      "fps": 30,
      "codec_id": "h264",
      "quality": "medium",
      "recording_mode": "continuous",
      "audio_enabled": false
    }],
    "retention_days": 30,
    "server_config": {
      "raid_type": "raid5",
      "failover_type": "none",
      "nic_capacity_mbps": 1000,
      "nic_count": 1
    }
  }'
```

## 📊 Calculation Methodology

### Storage Calculation
```
storage = bitrate × retention_days × 24 × 3600 × recording_factor
```
- `recording_factor`: 1.0 (continuous), 0.3-0.5 (motion), custom (scheduled)
- Includes RAID overhead and filesystem loss

### Server Count
```
servers = ceil(total_devices / 256) × failover_multiplier
```
- Max 256 devices per server
- Max 10 servers per site
- Failover: N+1 (2x), N+2 (3x)

### Bandwidth
```
total_bandwidth = sum(camera_bitrates) × 1.2  # 20% headroom
```

See [Calculation Methodology](docs/calculation-methodology.md) for detailed formulas.

## 🧪 Testing

**Run backend tests:**
```bash
cd backend
pytest --cov=app --cov-report=html
```

**Run frontend tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

**Run mutation tests:**
```bash
cd backend
mutmut run
```

## 📖 Documentation

- [Architecture Decision Records](docs/adr/)
- [API Documentation](http://localhost:8000/docs) (when running)
- [User Manual](docs/user-guide/README.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)

## 🔒 Security

- Input validation with Pydantic
- Rate limiting on API endpoints
- CORS configuration
- SQL injection prevention
- XSS protection
- Security scanning with Bandit

## 🎨 Customization

The calculator supports OEM white-labeling:
- Custom logo upload
- Brand colors
- Company name
- Custom disclaimers

Configuration files in `/config` allow customization without code changes:
- Camera resolutions
- Codec parameters
- RAID types
- Server specifications

## 📝 License

Copyright © 2025 Network Optix, Inc. All rights reserved.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📧 Support

For issues and questions, please contact:
- Technical Support: support@networkoptix.com
- Sales: sales@networkoptix.com

## 🏆 Quality Metrics

- Test Coverage: ≥85%
- Mutation Score: ≥70%
- Security Vulnerabilities: 0 high/critical
- Accessibility: WCAG 2.1 AA compliant
- Performance: <1s calculations, <5s PDF generation

