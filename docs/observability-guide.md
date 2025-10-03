# Observability & Monitoring Guide

**Nx System Calculator - Logging, Metrics, and Monitoring**

---

## Table of Contents

1. [Overview](#overview)
2. [Logging Strategy](#logging-strategy)
3. [Metrics & Monitoring](#metrics--monitoring)
4. [Error Tracking](#error-tracking)
5. [Performance Monitoring](#performance-monitoring)
6. [Alerting](#alerting)
7. [Dashboards](#dashboards)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Comprehensive observability ensures the Nx System Calculator runs reliably in production. This guide covers:

- **Structured Logging**: Consistent, searchable logs
- **Metrics Collection**: Performance and usage metrics
- **Error Tracking**: Automated error detection and reporting
- **Performance Monitoring**: Response times, throughput, resource usage
- **Alerting**: Proactive notification of issues
- **Dashboards**: Visual monitoring and analytics

---

## Logging Strategy

### Log Levels

The application uses standard Python logging levels:

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed diagnostic info | Variable values, function calls |
| INFO | General informational messages | Request received, calculation completed |
| WARNING | Warning messages | Deprecated feature used, high load |
| ERROR | Error messages | Calculation failed, database error |
| CRITICAL | Critical failures | Service unavailable, data corruption |

### Configuration

**Environment Variable:**
```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=INFO

# Troubleshooting
LOG_LEVEL=WARNING
```

### Structured Logging

**Format:**
```json
{
  "timestamp": "2025-10-03T12:34:56.789Z",
  "level": "INFO",
  "logger": "app.api.calculator",
  "message": "Calculation completed",
  "correlation_id": "req_abc123",
  "user_email": "john@example.com",
  "duration_ms": 245,
  "camera_count": 100,
  "server_count": 2
}
```

### Implementation

**Backend Logging:**

```python
# app/core/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def info(self, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "logger": self.logger.name,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

# Usage
logger = StructuredLogger(__name__)
logger.info(
    "Calculation completed",
    correlation_id=request_id,
    camera_count=100,
    duration_ms=245
)
```

### Log Correlation

**Correlation IDs:**
- Generate unique ID for each request
- Include in all log entries
- Pass to downstream services
- Return in response headers

**Example:**
```python
import uuid

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

### Log Storage

**Development:**
- Console output
- Local files: `logs/app.log`

**Production Options:**

1. **File-based with rotation:**
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
```

2. **Centralized logging:**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **AWS CloudWatch Logs**
- **Google Cloud Logging**
- **Azure Monitor**
- **Datadog**
- **Splunk**

---

## Metrics & Monitoring

### Key Metrics

#### Application Metrics

**Request Metrics:**
- Request count (total, per endpoint)
- Request duration (p50, p95, p99)
- Error rate (4xx, 5xx)
- Request size (bytes)
- Response size (bytes)

**Business Metrics:**
- Calculations performed
- Reports generated
- Emails sent
- Projects saved
- Average cameras per calculation
- Average retention days

**Resource Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Database connections

### Prometheus Integration

**Install Prometheus Client:**
```bash
pip install prometheus-client
```

**Instrumentation:**

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
calculations_total = Counter(
    'calculations_total',
    'Total calculations performed'
)

cameras_calculated = Histogram(
    'cameras_per_calculation',
    'Number of cameras per calculation',
    buckets=[10, 50, 100, 200, 500, 1000, 2000]
)

# Resource metrics
active_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

**Metrics Endpoint:**
```python
from prometheus_client import generate_latest

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Grafana Dashboards

**Sample Dashboard Panels:**

1. **Request Rate**
   - Query: `rate(http_requests_total[5m])`
   - Visualization: Graph

2. **Error Rate**
   - Query: `rate(http_requests_total{status=~"5.."}[5m])`
   - Visualization: Graph with alert threshold

3. **Response Time (p95)**
   - Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
   - Visualization: Graph

4. **Calculations per Hour**
   - Query: `rate(calculations_total[1h])`
   - Visualization: Stat

---

## Error Tracking

### Sentry Integration

**Install Sentry SDK:**
```bash
pip install sentry-sdk[fastapi]
```

**Configuration:**

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
    integrations=[FastApiIntegration()],
    before_send=filter_sensitive_data
)

def filter_sensitive_data(event, hint):
    # Remove sensitive data from error reports
    if 'request' in event:
        if 'headers' in event['request']:
            event['request']['headers'].pop('Authorization', None)
    return event
```

**Custom Error Context:**

```python
from sentry_sdk import capture_exception, set_context

try:
    result = calculate_system(data)
except Exception as e:
    set_context("calculation", {
        "camera_count": data.total_cameras,
        "retention_days": data.retention_days,
        "project_name": data.project.project_name
    })
    capture_exception(e)
    raise
```

### Error Alerting

**Sentry Alerts:**
- New error types
- Error frequency spikes
- Performance degradation
- Release health issues

**Configuration:**
- Slack/Email notifications
- PagerDuty integration
- Custom alert rules

---

## Performance Monitoring

### Application Performance Monitoring (APM)

**Options:**
- **Sentry Performance**
- **New Relic**
- **Datadog APM**
- **Elastic APM**

### Custom Performance Tracking

```python
# app/core/performance.py
import time
from functools import wraps

def track_performance(operation_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"{operation_name} completed",
                    duration_ms=duration * 1000,
                    success=True
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{operation_name} failed",
                    duration_ms=duration * 1000,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator

# Usage
@track_performance("system_calculation")
async def calculate_system(data):
    # Calculation logic
    pass
```

### Database Query Monitoring

```python
# app/core/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    if total > 1.0:  # Log slow queries (>1s)
        logger.warning(
            "Slow query detected",
            duration_ms=total * 1000,
            query=statement[:200]
        )
```

---

## Alerting

### Alert Rules

**Critical Alerts (PagerDuty):**
- Service down (health check fails)
- Error rate > 5%
- Database connection failures
- Disk space < 10%

**Warning Alerts (Slack/Email):**
- Response time p95 > 2s
- Error rate > 1%
- Memory usage > 80%
- Disk space < 20%

**Info Alerts (Email):**
- Daily usage summary
- Weekly performance report
- Backup completion

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    checks = {
        "database": check_database(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def check_database():
    try:
        db.execute("SELECT 1")
        return True
    except:
        return False
```

---

## Dashboards

### Grafana Dashboard Example

**Dashboard JSON:**
```json
{
  "dashboard": {
    "title": "Nx Calculator - Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

### Custom Analytics Dashboard

**Track:**
- Daily active users
- Calculations per day
- Average cameras per calculation
- Most common configurations
- Report generation rate
- Email delivery success rate

---

## Troubleshooting

### Common Monitoring Issues

**Issue: Metrics not appearing**
- Check `/metrics` endpoint is accessible
- Verify Prometheus scrape configuration
- Check firewall rules

**Issue: Logs not showing in centralized system**
- Verify log shipper is running
- Check network connectivity
- Validate log format

**Issue: Alerts not firing**
- Test alert rules manually
- Check notification channels
- Verify alert thresholds

---

## Best Practices

1. **Use correlation IDs** for request tracing
2. **Log at appropriate levels** (avoid DEBUG in production)
3. **Monitor business metrics** not just technical metrics
4. **Set up alerts** before issues occur
5. **Review dashboards regularly** to identify trends
6. **Test monitoring** in staging environment
7. **Document runbooks** for common alerts
8. **Rotate logs** to prevent disk fill
9. **Secure sensitive data** in logs and metrics
10. **Regular monitoring reviews** and improvements

---

## Support

For monitoring setup assistance:
- **Email**: support@networkoptix.com
- **Documentation**: https://docs.networkoptix.com
- **GitHub Issues**: https://github.com/networkoptix/nx_system_calc/issues

