# Deployment Guide

## Overview

This guide covers deployment options for the Math Homework Solver Backend API.

## Environment Configuration

### Production Environment Variables

Create a production `.env` file with the following variables:

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Firebase Configuration
FIREBASE_PROJECT_ID=your_production_project_id
FIREBASE_PRIVATE_KEY=your_production_service_account_private_key
FIREBASE_CLIENT_EMAIL=your_production_service_account_email
FIREBASE_STORAGE_BUCKET=your_production_storage_bucket

# OpenAI Configuration
OPENAI_API_KEY=your_production_openai_api_key

# API Configuration
API_TITLE=Math Homework Solver API
API_VERSION=1.0.0
API_DESCRIPTION=AI-powered math problem solver with OCR capabilities

# CORS Settings (adjust for your frontend domains)
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

## Docker Deployment

### Building the Docker Image

```bash
# Build the image
docker build -t math-solver-backend .

# Tag for registry (optional)
docker tag math-solver-backend your-registry/math-solver-backend:latest
```

### Running with Docker

```bash
# Run single container
docker run -d \
  --name math-solver-backend \
  -p 8000:8000 \
  --env-file .env \
  math-solver-backend

# Run with docker-compose
docker-compose up -d
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
```

## Cloud Deployment

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push to Container Registry**:
```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/math-solver-backend .
docker push gcr.io/YOUR_PROJECT_ID/math-solver-backend
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy math-solver-backend \
  --image gcr.io/YOUR_PROJECT_ID/math-solver-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars ENVIRONMENT=production,DEBUG=false \
  --set-env-vars FIREBASE_PROJECT_ID=your_project_id \
  --set-env-vars OPENAI_API_KEY=your_api_key
```

#### Using App Engine

1. Create `app.yaml`:
```yaml
runtime: python311
service: default

env_variables:
  ENVIRONMENT: production
  DEBUG: false
  FIREBASE_PROJECT_ID: your_project_id
  OPENAI_API_KEY: your_api_key

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
```

2. Deploy:
```bash
gcloud app deploy
```

### AWS Deployment

#### Using ECS with Fargate

1. **Create ECS task definition**:
```json
{
  "family": "math-solver-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "math-solver-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/math-solver-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DEBUG", "value": "false"}
      ],
      "secrets": [
        {
          "name": "FIREBASE_PROJECT_ID",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:firebase-project-id"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-api-key"
        }
      ]
    }
  ]
}
```

#### Using Elastic Beanstalk

1. Create `Dockerrun.aws.json`:
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "your-account.dkr.ecr.region.amazonaws.com/math-solver-backend:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ]
}
```

2. Deploy using EB CLI:
```bash
eb init
eb create production-env
eb deploy
```

## Kubernetes Deployment

### Deployment Configuration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: math-solver-backend
  labels:
    app: math-solver-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: math-solver-backend
  template:
    metadata:
      labels:
        app: math-solver-backend
    spec:
      containers:
      - name: math-solver-backend
        image: your-registry/math-solver-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DEBUG
          value: "false"
        - name: FIREBASE_PROJECT_ID
          valueFrom:
            secretKeyRef:
              name: firebase-secrets
              key: project-id
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: math-solver-backend-service
spec:
  selector:
    app: math-solver-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Secrets Management

```yaml
# k8s-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: firebase-secrets
type: Opaque
data:
  project-id: <base64-encoded-project-id>
  private-key: <base64-encoded-private-key>
  client-email: <base64-encoded-client-email>
---
apiVersion: v1
kind: Secret
metadata:
  name: openai-secrets
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

## Reverse Proxy Configuration

### Nginx Configuration

```nginx
# nginx.conf
upstream backend {
    server api:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # File upload size limit
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Health Checks

The API provides a health check endpoint at `/health`. Configure your load balancer or orchestrator to use this endpoint.

### Logging

Configure structured logging for production:

```python
# In production configuration
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/app.log')
    ]
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(JSONFormatter())
```

### Metrics

Consider integrating with monitoring services:
- **Prometheus**: For metrics collection
- **Grafana**: For visualization
- **Sentry**: For error tracking
- **New Relic**: For APM

## Security Considerations

### Environment Security

1. **Never commit secrets to version control**
2. **Use secret management services** (AWS Secrets Manager, Google Secret Manager, etc.)
3. **Rotate API keys regularly**
4. **Use least privilege principle** for service accounts

### Network Security

1. **Use HTTPS only** in production
2. **Configure CORS properly** for your frontend domains
3. **Implement rate limiting** to prevent abuse
4. **Use Web Application Firewall (WAF)** if available

### Firebase Security

1. **Configure Firestore security rules**:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/solutions/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

2. **Set up Firebase App Check** for additional security

## Scaling Considerations

### Horizontal Scaling

The application is stateless and can be scaled horizontally:
- Use load balancers to distribute traffic
- Scale based on CPU/memory usage
- Consider auto-scaling groups

### Database Scaling

- Firestore scales automatically
- Monitor usage and costs
- Consider data archiving for old problems

### Caching

Consider implementing caching for:
- Frequently accessed user data
- AI model responses (with user consent)
- Static configuration data

## Backup and Disaster Recovery

### Database Backups

Firestore provides automatic backups, but consider:
- Regular exports to Cloud Storage
- Cross-region replication for critical data
- Testing restore procedures

### Application Backups

- Container images in multiple registries
- Configuration backups
- SSL certificate backups

## Performance Optimization

### Application Performance

1. **Use async/await** throughout the application
2. **Implement connection pooling** for external services
3. **Optimize AI model calls** (batching, caching)
4. **Monitor and profile** regularly

### Infrastructure Performance

1. **Use CDN** for static assets
2. **Configure proper caching headers**
3. **Optimize container images** (multi-stage builds)
4. **Use performance monitoring tools**

## Troubleshooting Deployment Issues

### Common Issues

1. **Environment variables not set**: Check secret management
2. **Port binding issues**: Ensure port 8000 is exposed
3. **Firebase connection**: Verify service account permissions
4. **OpenAI API limits**: Check usage and rate limits
5. **Memory issues**: Monitor and adjust resource limits

### Debugging Tools

```bash
# Check container logs
docker logs math-solver-backend

# Check resource usage
docker stats

# Test health endpoint
curl http://localhost:8000/health

# Check environment variables
docker exec -it math-solver-backend env
```

## Maintenance

### Regular Tasks

1. **Update dependencies** regularly
2. **Monitor security advisories**
3. **Review logs** for errors and performance issues
4. **Update SSL certificates**
5. **Test backup and restore procedures**

### Monitoring Checklist

- [ ] Application health checks
- [ ] Resource usage (CPU, memory, disk)
- [ ] API response times
- [ ] Error rates
- [ ] External service availability (Firebase, OpenAI)
- [ ] SSL certificate expiration
- [ ] Security scan results
