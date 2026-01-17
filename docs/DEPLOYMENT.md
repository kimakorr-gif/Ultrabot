# Deployment Guide

## Local Development with Docker Compose

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM, 10GB disk space available

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ultrabot
cd ultrabot

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker exec ultrabot-postgres psql -U ultrabot -d ultrabot -f /migrations/init.sql

# 5. Check health
curl http://localhost:8000/health
curl http://localhost:9090/metrics
```

### Access Points
- **API**: http://localhost:8000
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin:admin)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Stopping Services

```bash
docker-compose down -v  # -v removes volumes
```

---

## Production Deployment (Kubernetes)

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Container registry access
- PostgreSQL external or in-cluster
- Redis external or in-cluster

### 1. Build and Push Docker Image

```bash
# Build image
docker build -f docker/Dockerfile -t myregistry/ultrabot:1.0.0 .

# Push to registry
docker push myregistry/ultrabot:1.0.0
```

### 2. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace ultrabot

# Create secrets
kubectl -n ultrabot create secret generic ultrabot-secrets \
  --from-literal=telegram_token=YOUR_TOKEN \
  --from-literal=yandex_api_key=YOUR_KEY \
  --from-literal=database_url="postgresql://user:pass@postgres-host:5432/ultrabot"
```

### 3. Update ConfigMap

Edit `kubernetes/configmap.yaml` with your environment variables:

```yaml
data:
  telegram_channel_id: "-1001234567890"
  redis_url: "redis://redis-host:6379/0"
  rss_check_interval: "300"
  min_score_threshold: "8"
```

### 4. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Verify deployment
kubectl -n ultrabot get pods
kubectl -n ultrabot get svc
kubectl -n ultrabot get hpa

# Check logs
kubectl -n ultrabot logs -f deployment/ultrabot
```

### 5. Setup Ingress (Optional)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ultrabot-ingress
  namespace: ultrabot
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - ultrabot.example.com
      secretName: ultrabot-tls
  rules:
    - host: ultrabot.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ultrabot
                port:
                  number: 8000
```

### 6. Verify Deployment

```bash
# Health check
kubectl -n ultrabot port-forward svc/ultrabot 8000:8000
curl http://localhost:8000/health

# Metrics
kubectl -n ultrabot port-forward svc/ultrabot 9090:9090
# Access http://localhost:9090/metrics
```

### 7. Monitor with Prometheus

```bash
# Port forward to Prometheus
kubectl -n ultrabot port-forward svc/prometheus 9090:9090

# Access http://localhost:9090
```

---

## Database Migrations

### Using Alembic

```bash
# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Manual Migration (Kubernetes)

```bash
# Connect to PostgreSQL pod
kubectl -n ultrabot exec -it postgres-pod -- psql -U ultrabot -d ultrabot

# Run SQL migrations
\i migrations/001_init.sql
```

---

## Scaling

### Horizontal Scaling

The deployment includes HorizontalPodAutoscaler:
- Min replicas: 2
- Max replicas: 5
- CPU target: 70%
- Memory target: 80%

```bash
# Check HPA status
kubectl -n ultrabot get hpa
kubectl -n ultrabot describe hpa ultrabot
```

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl -n ultrabot scale deployment ultrabot --replicas=5
```

---

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl -n ultrabot describe pod ultrabot-xxx

# Check logs
kubectl -n ultrabot logs ultrabot-xxx
```

### Database connection issues

```bash
# Test PostgreSQL connection
kubectl -n ultrabot exec -it ultrabot-xxx -- \
  psql postgresql://user:pass@postgres:5432/ultrabot

# Check database DNS
kubectl -n ultrabot run test-dns --image=busybox --rm -it -- nslookup postgres
```

### Redis connectivity

```bash
# Test Redis connection
kubectl -n ultrabot exec -it ultrabot-xxx -- \
  redis-cli -h redis ping
```

### Check resource usage

```bash
# Pod resource usage
kubectl -n ultrabot top pods

# Node resource usage
kubectl top nodes
```

---

## Backups

### Database Backup

```bash
# Manual backup
kubectl -n ultrabot exec postgres-pod -- \
  pg_dump -U ultrabot ultrabot > backup.sql

# Restore from backup
kubectl -n ultrabot exec postgres-pod -- \
  psql -U ultrabot ultrabot < backup.sql
```

### Automated Backups (Recommended)

Use cloud provider's automated backup service:
- AWS RDS automated backups
- GCP Cloud SQL automated backups
- Azure Database automated backups

---

## Upgrade Process

### Rolling Update

```bash
# Update image tag in deployment
kubectl -n ultrabot set image deployment/ultrabot \
  ultrabot=myregistry/ultrabot:2.0.0

# Monitor rollout
kubectl -n ultrabot rollout status deployment/ultrabot
```

### Rollback

```bash
# Rollback last update
kubectl -n ultrabot rollout undo deployment/ultrabot

# See revision history
kubectl -n ultrabot rollout history deployment/ultrabot
```

---

## Cost Optimization

### Resource Limits

Recommended for $50/month budget:
- **CPU**: 250m request, 500m limit per pod
- **Memory**: 256Mi request, 512Mi limit per pod
- **Replicas**: 2-5 based on autoscaling

### Cost Estimation

For small scale (2-3 pods):
- Compute: ~$20/month
- Database: ~$15/month
- Kubernetes: ~$15/month (if self-hosted)
- **Total**: ~$50/month

---

## Support & Monitoring

See [MONITORING.md](MONITORING.md) for:
- Prometheus setup
- Alert configuration
- Grafana dashboards
- Log aggregation
