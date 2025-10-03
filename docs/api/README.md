# Nx System Calculator API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (development) | `https://your-domain.com` (production)  
**API Prefix:** `/api/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
6. [Request/Response Examples](#request-response-examples)
7. [OpenAPI Specification](#openapi-specification)

---

## Overview

The Nx System Calculator API provides RESTful endpoints for:
- **System Calculations**: Calculate server, storage, and bandwidth requirements
- **Configuration Management**: Retrieve resolution, codec, RAID, and server presets
- **Project Management**: Save, retrieve, and manage calculation projects
- **Report Generation**: Generate and email PDF reports
- **OEM Branding**: Upload logos and customize branding
- **Webhooks**: Receive notifications for calculation events

### Key Features

- ✅ **Auto-generated Documentation**: Interactive docs at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- ✅ **Type Validation**: Pydantic schemas ensure data integrity
- ✅ **CORS Support**: Configurable cross-origin resource sharing
- ✅ **Health Checks**: `/health` endpoint for monitoring
- ✅ **Versioned API**: `/api/v1` prefix for future compatibility

---

## Authentication

**Current Version:** No authentication required (v1.0.0)

**Future Versions:** Will support:
- API Key authentication via `X-API-Key` header
- JWT tokens for user-specific operations
- OAuth2 for third-party integrations

---

## Rate Limiting

**Default Limits:**
- 60 requests per minute per IP address
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1633024800
```

**429 Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-10-03T12:34:56Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `CALCULATION_ERROR`: Calculation logic error
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `INVALID_FILE_TYPE`: Unsupported file format

---

## Endpoints

### 1. System Calculations

#### `POST /api/v1/calculate`

Calculate system requirements based on camera configuration.

**Request Body:**
```json
{
  "project": {
    "project_name": "Downtown Surveillance",
    "created_by": "John Doe",
    "creator_email": "john@example.com",
    "company_name": "Acme Security"
  },
  "camera_groups": [
    {
      "num_cameras": 100,
      "resolution_id": "2mp_1080p",
      "fps": 30,
      "codec_id": "h264",
      "quality": "medium",
      "recording_mode": "continuous",
      "audio_enabled": false
    }
  ],
  "retention_days": 30,
  "server_config": {
    "raid_type": "raid5",
    "failover_type": "none",
    "nic_capacity_mbps": 1000,
    "nic_count": 1
  }
}
```

**Response:** `200 OK`
```json
{
  "project_info": {
    "project_name": "Downtown Surveillance",
    "created_by": "John Doe",
    "total_cameras": 100
  },
  "bandwidth": {
    "average_mbps": 245.5,
    "peak_mbps": 294.6,
    "required_nic_count": 1
  },
  "storage": {
    "total_tb": 12.5,
    "usable_tb": 10.2,
    "raid_overhead_percent": 18.4
  },
  "servers": {
    "required_count": 1,
    "recommended_spec": "mid_range",
    "per_server_cameras": 100
  },
  "licenses": {
    "total_required": 100,
    "per_server": 100
  }
}
```

---

### 2. Configuration Endpoints

#### `GET /api/v1/config/resolutions`

Get available camera resolution presets.

**Response:** `200 OK`
```json
{
  "resolutions": [
    {
      "id": "2mp_1080p",
      "name": "2MP (1920x1080)",
      "width": 1920,
      "height": 1080,
      "megapixels": 2.07
    }
  ]
}
```

#### `GET /api/v1/config/codecs`

Get available codec configurations.

**Response:** `200 OK`
```json
{
  "codecs": [
    {
      "id": "h264",
      "name": "H.264",
      "compression_ratio": 0.5,
      "quality_factor": 1.0
    }
  ]
}
```

#### `GET /api/v1/config/raid-types`

Get RAID type configurations.

**Response:** `200 OK`
```json
{
  "raid_types": [
    {
      "id": "raid5",
      "name": "RAID 5",
      "min_drives": 3,
      "overhead_percent": 33.3,
      "fault_tolerance": 1
    }
  ]
}
```

#### `GET /api/v1/config/server-specs`

Get server specification presets.

**Response:** `200 OK`
```json
{
  "specs": [
    {
      "id": "mid_range",
      "name": "Mid-Range Server",
      "max_cameras": 256,
      "cpu_cores": 8,
      "ram_gb": 32,
      "estimated_cost_usd": 3500
    }
  ],
  "constraints": {
    "max_cameras_per_server": 256,
    "max_servers_per_site": 10
  }
}
```

---

### 3. Project Management

#### `POST /api/v1/projects`

Save a calculation project.

**Request Body:**
```json
{
  "project_name": "Downtown Surveillance",
  "created_by": "John Doe",
  "creator_email": "john@example.com",
  "calculation_data": { /* full calculation request */ },
  "results": { /* calculation results */ }
}
```

**Response:** `201 Created`
```json
{
  "id": "proj_abc123",
  "project_name": "Downtown Surveillance",
  "created_at": "2025-10-03T12:34:56Z",
  "updated_at": "2025-10-03T12:34:56Z"
}
```

#### `GET /api/v1/projects/{project_id}`

Retrieve a saved project.

**Response:** `200 OK`
```json
{
  "id": "proj_abc123",
  "project_name": "Downtown Surveillance",
  "created_by": "John Doe",
  "calculation_data": { /* original request */ },
  "results": { /* calculation results */ },
  "created_at": "2025-10-03T12:34:56Z"
}
```

#### `GET /api/v1/projects`

List all projects (with pagination).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "total": 45,
  "skip": 0,
  "limit": 20,
  "projects": [
    {
      "id": "proj_abc123",
      "project_name": "Downtown Surveillance",
      "created_by": "John Doe",
      "created_at": "2025-10-03T12:34:56Z"
    }
  ]
}
```

---

### 4. Report Generation

#### `POST /api/v1/generate-report`

Generate a PDF report.

**Request Body:**
```json
{
  "calculation_data": { /* full calculation request */ },
  "results": { /* calculation results */ },
  "branding": {
    "logo_url": "/uploads/logos/company-logo.png",
    "company_name": "Acme Security",
    "primary_color": "#0066cc"
  }
}
```

**Response:** `200 OK`
```json
{
  "report_url": "/reports/report_abc123.pdf",
  "report_id": "report_abc123",
  "generated_at": "2025-10-03T12:34:56Z",
  "file_size_bytes": 245678
}
```

#### `POST /api/v1/email/send-report`

Generate and email a PDF report.

**Request Body:**
```json
{
  "recipient_email": "customer@example.com",
  "recipient_name": "Jane Smith",
  "calculation_data": { /* full calculation request */ },
  "results": { /* calculation results */ },
  "message": "Here is your system calculation report.",
  "branding": { /* optional branding */ }
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Report sent successfully",
  "report_url": "/reports/report_abc123.pdf",
  "sent_to": "customer@example.com",
  "bcc_to": "sales@networkoptix.com"
}
```

---

### 5. OEM Branding

#### `POST /api/v1/branding/upload-logo`

Upload a company logo.

**Request:** `multipart/form-data`
- `file`: Image file (JPG, PNG, SVG, max 5MB)

**Response:** `200 OK`
```json
{
  "logo_url": "/uploads/logos/logo_abc123.png",
  "filename": "company-logo.png",
  "size_bytes": 45678
}
```

---

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **JSON Spec**: `http://localhost:8000/openapi.json`

### Download OpenAPI Spec

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

---

## SDK & Client Libraries

### Python Client Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Calculate system requirements
response = requests.post(f"{API_BASE}/calculate", json={
    "project": {
        "project_name": "Test Project",
        "created_by": "John Doe",
        "creator_email": "john@example.com"
    },
    "camera_groups": [{
        "num_cameras": 50,
        "resolution_id": "2mp_1080p",
        "fps": 30,
        "codec_id": "h264",
        "quality": "medium",
        "recording_mode": "continuous",
        "audio_enabled": False
    }],
    "retention_days": 30,
    "server_config": {
        "raid_type": "raid5",
        "failover_type": "none",
        "nic_capacity_mbps": 1000,
        "nic_count": 1
    }
})

results = response.json()
print(f"Required servers: {results['servers']['required_count']}")
print(f"Total storage: {results['storage']['total_tb']} TB")
```

### JavaScript/TypeScript Client Example

```typescript
const API_BASE = 'http://localhost:8000/api/v1';

async function calculateSystem() {
  const response = await fetch(`${API_BASE}/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project: {
        project_name: 'Test Project',
        created_by: 'John Doe',
        creator_email: 'john@example.com'
      },
      camera_groups: [{
        num_cameras: 50,
        resolution_id: '2mp_1080p',
        fps: 30,
        codec_id: 'h264',
        quality: 'medium',
        recording_mode: 'continuous',
        audio_enabled: false
      }],
      retention_days: 30,
      server_config: {
        raid_type: 'raid5',
        failover_type: 'none',
        nic_capacity_mbps: 1000,
        nic_count: 1
      }
    })
  });
  
  const results = await response.json();
  console.log(`Required servers: ${results.servers.required_count}`);
  console.log(`Total storage: ${results.storage.total_tb} TB`);
}
```

---

## Support & Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **GitHub Repository**: https://github.com/networkoptix/nx_system_calc
- **Issue Tracker**: https://github.com/networkoptix/nx_system_calc/issues
- **Email Support**: support@networkoptix.com

