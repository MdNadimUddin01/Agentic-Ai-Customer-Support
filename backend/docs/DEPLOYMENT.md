# Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Minimum 4GB RAM, 10GB disk space

## Local Development Setup

### 1. Clone and Setup

```bash
# Navigate to project directory
cd nadim-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# Google Gemini API (REQUIRED)
GOOGLE_API_KEY=your-gemini-api-key-here

# MongoDB (default for local)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=ai_support_system

# Redis (default for local)
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 3. Start Infrastructure Services

```bash
# Start MongoDB and Redis with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Create indexes and verify setup
python scripts/init_db.py

# Seed sample data (knowledge base, customers, etc.)
python scripts/seed_data.py
```

### 5. Start API Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m src.api.main
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 6. Verify Installation

```bash
# Health check
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I cant login to my account",
    "customer_id": "cust_001"
  }'
```

---

## Production Deployment

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

**1. Update docker-compose.yml**

Uncomment the API service in `docker-compose.yml`:

```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: ai_support_api
  ports:
    - "8000:8000"
  environment:
    - MONGODB_URI=mongodb://mongodb:27017
    - REDIS_HOST=redis
  env_file:
    - .env
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy
  networks:
    - ai_support_network
  restart: unless-stopped
```

**2. Build and Deploy**

```bash
# Build Docker image
docker-compose build api

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Scale API instances
docker-compose up -d --scale api=3
```

**3. Initialize Production Database**

```bash
# Run initialization in container
docker-compose exec api python scripts/init_db.py
docker-compose exec api python scripts/seed_data.py
```

### Option 2: Kubernetes (For Large Scale)

**1. Create Kubernetes Manifests**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-support-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-support-api
  template:
    metadata:
      labels:
        app: ai-support-api
    spec:
      containers:
      - name: api
        image: your-registry/ai-support-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: gemini-api-key
        - name: MONGODB_URI
          value: "mongodb://mongo-service:27017"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-support-api
spec:
  selector:
    app: ai-support-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**2. Deploy to Kubernetes**

```bash
# Create secrets
kubectl create secret generic api-secrets \
  --from-literal=gemini-api-key='your-key'

# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get svc
```

### Option 3: Cloud Platforms

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 ai-support-system

# Create environment
eb create production

# Deploy
eb deploy

# Set environment variables
eb setenv GOOGLE_API_KEY=your-key
```

#### Google Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-support-api

# Deploy
gcloud run deploy ai-support-api \
  --image gcr.io/PROJECT_ID/ai-support-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your-key
```

#### Azure App Service

```bash
# Login
az login

# Create app
az webapp up --name ai-support-api \
  --runtime "PYTHON:3.11" \
  --sku B1

# Set environment variables
az webapp config appsettings set \
  --name ai-support-api \
  --settings GOOGLE_API_KEY=your-key
```

---

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. **Create Cluster:**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create free or paid cluster
   - Select region close to your users

2. **Configure:**
   - Whitelist IP addresses or allow all (0.0.0.0/0)
   - Create database user
   - Get connection string

3. **Update Configuration:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_support_system
```

4. **Enable Vector Search:**
   - Go to Atlas Search
   - Create search index on `knowledge_base` collection
   - Index `embedding` field as vector type

### Self-Hosted MongoDB

```bash
# Install MongoDB 7.0
# Ubuntu/Debian:
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Secure MongoDB
mongo
> use admin
> db.createUser({user: "admin", pwd: "strong_password", roles: ["root"]})
> exit

# Enable authentication in /etc/mongod.conf:
security:
  authorization: enabled
```

---

## Redis Setup

### Cloud Redis

**AWS ElastiCache:**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id ai-support-cache \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

**Azure Redis:**
```bash
az redis create \
  --name ai-support-cache \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Self-Hosted Redis

```bash
# Install Redis
sudo apt-get install redis-server

# Configure in /etc/redis/redis.conf:
# bind 127.0.0.1
# requirepass your_strong_password

# Restart
sudo systemctl restart redis
```

---

## Environment Variables (Production)

```bash
# Application
APP_NAME=AI Customer Support System
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=<generate-secure-key-here>
CORS_ORIGINS=["https://yourdomain.com"]

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
MONGODB_DB_NAME=ai_support_system
MONGODB_MAX_POOL_SIZE=50

# Redis
REDIS_HOST=your-redis-host.cloud
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Google Gemini
GOOGLE_API_KEY=your-production-api-key
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7

# Features
ENABLE_WHATSAPP=true
ENABLE_WEB_CHAT=true
ENABLE_REAL_INTEGRATIONS=true

# Integrations (if using real services)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
STRIPE_API_KEY=sk_live_your-stripe-key
```

---

## Security Checklist

- [ ] Use strong `API_SECRET_KEY` (generate with `openssl rand -hex 32`)
- [ ] Enable HTTPS (use Let's Encrypt or cloud provider SSL)
- [ ] Restrict CORS origins to your domains
- [ ] Use MongoDB authentication
- [ ] Enable Redis password
- [ ] Store secrets in environment variables or secret manager
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Enable rate limiting in production
- [ ] Set up monitoring and alerts
- [ ] Regular database backups
- [ ] Implement API authentication (JWT)

---

## Monitoring

### Application Logs

```bash
# View logs
tail -f logs/app.log

# Error logs
tail -f logs/errors.log

# In production, use log aggregation:
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - Datadog
# - CloudWatch (AWS)
```

### Health Checks

```bash
# API health
curl http://your-domain.com/api/health

# Uptime monitoring with:
# - UptimeRobot
# - Pingdom
# - StatusCake
```

### Metrics to Track

- Request rate (requests/minute)
- Response time (p50, p95, p99)
- Error rate (5xx errors)
- Agent success rate
- Escalation rate
- Database query performance
- Memory/CPU usage

### Example Grafana Dashboard

```python
# Expose metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('requests_total', 'Total requests')
response_time = Histogram('response_time_seconds', 'Response time')
escalation_count = Counter('escalations_total', 'Total escalations')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale api=5

# Kubernetes
kubectl scale deployment ai-support-api --replicas=10

# AWS
eb scale 5
```

### Database Sharding

For large scale (10M+ customers), shard MongoDB by customer_id:

```javascript
// Enable sharding
sh.enableSharding("ai_support_system")

// Shard conversations collection
sh.shardCollection(
  "ai_support_system.conversations",
  { "customer_id": "hashed" }
)
```

### Caching Strategy

- Cache conversation state in Redis
- Cache customer profiles (TTL: 2 hours)
- Cache knowledge base results (TTL: 24 hours)

---

## Backup and Disaster Recovery

### MongoDB Backups

```bash
# Manual backup
mongodump --uri="mongodb://localhost:27017/ai_support_system" --out=/backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/ai_support_system" /backup/ai_support_system/

# Automated backups (Atlas)
# Configure in Atlas UI: Backup > Enable Continuous Backup
```

### Application State

- Stateless API design (no local state)
- All state in MongoDB/Redis
- Can restart/replace instances anytime

---

## Troubleshooting

### API Won't Start

```bash
# Check logs
tail -f logs/app.log

# Common issues:
# 1. MongoDB not running
docker-compose ps mongodb
# 2. Missing GOOGLE_API_KEY
echo $GOOGLE_API_KEY
# 3. Port already in use
lsof -i :8000
```

### Database Connection Errors

```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017

# Check firewall
sudo ufw status

# Verify credentials in .env
```

### High Memory Usage

- Reduce MAX_CONVERSATION_HISTORY
- Clear Redis cache
- Restart API periodically
- Increase instance size

### Slow Response Times

- Check database query performance
- Optimize knowledge base searches
- Increase Redis cache TTL
- Add database indexes
- Scale horizontally

---

## Maintenance

### Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Test in staging first
# Deploy to production

# Database migrations (if schema changes)
python scripts/migrate.py
```

### Monitoring Checklist

- [ ] Check error logs daily
- [ ] Review escalation rate weekly
- [ ] Monitor database size
- [ ] Test backups monthly
- [ ] Update dependencies quarterly
- [ ] Review and rotate API keys
- [ ] Check SSL certificate expiry

---

## Support

For deployment issues:
1. Check logs in `logs/` directory
2. Review documentation: `/docs`
3. Create issue on GitHub
4. Contact: support@example.com
