# Deployment Guide

## Overview

This guide covers deploying the DSX Documentation Assistant to various environments:
- Local development
- Docker containers
- GitHub Actions CI/CD
- Cloud platforms (Azure, AWS, etc.)

---

## Docker Deployment

### Single Container (Development/Testing)

#### Build the Image

```powershell
# Navigate to project root
cd dsx-doc-assistant

# Build image
docker build -t dsx-doc-assistant:latest .

# Verify build
docker images | grep dsx-doc-assistant
```

#### Run Container

```powershell
# Create data directory for persistence
mkdir data -Force

# Run with environment variables
docker run -d `
  --name dsx-assistant `
  -p 8501:8501 `
  -e DSX_API_KEY="sk-your-key-here" `
  -e DSX_CHAT_MODEL="openai/gpt-oss-120b" `
  -v ${PWD}/dsx_files_input:/app/dsx_files_input `
  -v ${PWD}/data:/app/data `
  --restart unless-stopped `
  dsx-doc-assistant:latest

# Check container status
docker ps | grep dsx-assistant

# View logs
docker logs -f dsx-assistant

# Stop container
docker stop dsx-assistant

# Clean up
docker rm dsx-assistant
```

#### Access Application

- **URL**: http://localhost:8501
- **Database location**: `./data/dsx_graph_all.sqlite`
- **Generated docs**: Stored in database (export via UI)

### Docker Compose (Production-Ready)

#### Setup

```powershell
# Create .env file
cat > .env << 'EOF'
DSX_API_KEY=sk-your-key-here
DSX_CHAT_MODEL=openai/gpt-oss-120b
DSX_CHAT_BASE_URL=https://openrouter.ai/api/v1
DSX_CHAT_PROVIDER=openrouter
EOF

# Create data directory
mkdir data -Force
```

#### Start Services

```powershell
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
docker-compose ps

# Stop services
docker-compose down

# Clean up including volumes
docker-compose down -v
```

#### docker-compose.yml Configuration

The provided `docker-compose.yml` includes:

```yaml
version: '3.8'
services:
  dsx-doc-assistant:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DSX_API_KEY=${DSX_API_KEY}
      - DSX_MODEL=${DSX_MODEL:-openai/text-embedding-3-small}
      - DSX_BASE_URL=${DSX_BASE_URL:-https://openrouter.ai/api/v1}
      - DSX_PROVIDER=${DSX_PROVIDER:-openrouter}
    volumes:
      - ./data:/app/data
      - ./dsx_files_input:/app/dsx_files_input
    restart: unless-stopped
```

**Key points:**
- Port `8501` exposed for web access
- `./data` volume persists SQLite database
- `./dsx_files_input` volume for easy file updates
- Auto-restart on container failure

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (EKS, AKS, GKE, Minikube, etc.)
- `kubectl` configured
- Docker image pushed to registry

### Create Deployment Manifest

**File: `k8s/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dsx-doc-assistant
  labels:
    app: dsx-assistant
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dsx-assistant
  template:
    metadata:
      labels:
        app: dsx-assistant
    spec:
      containers:
      - name: dsx-assistant
        image: your-registry/dsx-doc-assistant:latest
        ports:
        - containerPort: 8501
        env:
        - name: DSX_API_KEY
          valueFrom:
            secretKeyRef:
              name: dsx-secrets
              key: api-key
        - name: DSX_CHAT_MODEL
          value: "openai/gpt-oss-120b"
        - name: DSX_CHAT_BASE_URL
          value: "https://openrouter.ai/api/v1"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: dsx-files
          mountPath: /app/dsx_files_input
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: dsx-data-pvc
      - name: dsx-files
        persistentVolumeClaim:
          claimName: dsx-files-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: dsx-assistant-service
spec:
  selector:
    app: dsx-assistant
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dsx-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dsx-files-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

### Create Secrets

```bash
# Create secret for API key
kubectl create secret generic dsx-secrets \
  --from-literal=api-key="sk-your-key-here"
```

### Deploy

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get deployments
kubectl get services
kubectl get pods

# View logs
kubectl logs -f deployment/dsx-doc-assistant

# Access application
# Get LoadBalancer IP
kubectl get service dsx-assistant-service
# Open browser to http://EXTERNAL-IP
```

---

## AWS Deployment

### Option 1: ECS (Elastic Container Service)

**Task Definition (CloudFormation)**:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  DSXDocAssistantCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: dsx-doc-assistant

  DSXDocAssistantTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: dsx-doc-assistant
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: '256'
      Memory: '512'
      ContainerDefinitions:
        - Name: dsx-doc-assistant
          Image: your-registry/dsx-doc-assistant:latest
          PortMappings:
            - ContainerPort: 8501
              Protocol: tcp
          Environment:
            - Name: DSX_CHAT_MODEL
              Value: openai/gpt-oss-120b
          Secrets:
            - Name: DSX_API_KEY
              ValueFrom: arn:aws:secretsmanager:region:account:secret:dsx-api-key

  DSXDocAssistantService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: dsx-doc-assistant-service
      Cluster: !Ref DSXDocAssistantCluster
      TaskDefinition: !Ref DSXDocAssistantTaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: [subnet-xxx, subnet-yyy]
          SecurityGroups: [sg-xxx]
          AssignPublicIp: ENABLED
```

### Option 2: App Runner (Easier)

```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag dsx-doc-assistant:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/dsx-doc-assistant:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/dsx-doc-assistant:latest

# Create App Runner service via AWS Console or CLI
aws apprunner create-service \
  --service-name dsx-doc-assistant \
  --source-configuration ImageRepository={ImageIdentifier=123456789.dkr.ecr.us-east-1.amazonaws.com/dsx-doc-assistant:latest,ImageRepositoryType=ECR}
```

---

## Azure Deployment

### Option 1: Azure Container Instances (ACI)

```bash
# Create resource group
az group create --name dsx-rg --location eastus

# Push image to ACR
az acr login --name your-registry
docker tag dsx-doc-assistant:latest your-registry.azurecr.io/dsx-doc-assistant:latest
docker push your-registry.azurecr.io/dsx-doc-assistant:latest

# Deploy to ACI
az container create \
  --resource-group dsx-rg \
  --name dsx-assistant \
  --image your-registry.azurecr.io/dsx-doc-assistant:latest \
  --cpu 1 --memory 1 \
  --registry-login-server your-registry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8501 \
  --environment-variables \
    DSX_API_KEY="sk-..." \
    DSX_CHAT_MODEL="openai/gpt-oss-120b" \
  --dns-name-label dsx-assistant

# Get status
az container show --resource-group dsx-rg --name dsx-assistant
```

### Option 2: App Service (with Container Support)

```bash
# Create App Service Plan
az appservice plan create \
  --name dsx-plan \
  --resource-group dsx-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group dsx-rg \
  --plan dsx-plan \
  --name dsx-doc-assistant \
  --deployment-container-image-name your-registry.azurecr.io/dsx-doc-assistant:latest

# Configure
az webapp config container set \
  --name dsx-doc-assistant \
  --resource-group dsx-rg \
  --docker-custom-image-name your-registry.azurecr.io/dsx-doc-assistant:latest \
  --docker-registry-server-url https://your-registry.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>

# Set environment variables
az webapp config appsettings set \
  --resource-group dsx-rg \
  --name dsx-doc-assistant \
  --settings DSX_API_KEY="sk-..." DSX_CHAT_MODEL="openai/gpt-oss-120b"
```

---

## GitHub Actions CI/CD

See [GITHUB_AUTOMATION_SETUP.md](../GITHUB_AUTOMATION_SETUP.md) for detailed setup.

**Quick overview:**
- Automatically generates docs when `.dsx` files are pushed
- Commits generated documentation back to repo
- Supports secrets management
- No manual intervention needed

---

## Monitoring & Health Checks

### Health Check Endpoint

```bash
# Check if application is healthy
curl http://localhost:8501/_stcore/health

# Expected response
{"ok": true}
```

### Docker Health Check

```bash
# View health status
docker inspect --format='{{.State.Health.Status}}' dsx-assistant

# Logs
docker inspect --format='{{json .State.Health.Log}}' dsx-assistant | jq
```

### Logs & Debugging

```bash
# Docker
docker logs dsx-assistant

# Docker Compose
docker-compose logs dsx-doc-assistant

# Kubernetes
kubectl logs -f deployment/dsx-doc-assistant
kubectl describe pod <pod-name>

# Application logs
# Check stdout in container for Streamlit logs
```

---

## Performance Tuning

### Resource Requirements

| Component | Memory | CPU | Storage |
|-----------|--------|-----|---------|
| Base Image | 256MB | 0.1 | 500MB |
| Runtime | 400MB+ | 0.2+ | N/A |
| Database | 100MB per 1000 jobs | N/A | Linear |
| **Total (Recommended)** | 1GB | 0.5 | 5GB |

### Environment Variables for Tuning

```env
# Timeout (slower connections)
DSX_CHAT_TIMEOUT_SEC=300

# Faster model (trades quality)
DSX_CHAT_MODEL=openai/gpt-3.5-turbo

# Concurrent workers for CLI
DSX_DOCS_MAX_WORKERS=4

# Retry settings
DSX_CHAT_MAX_RETRIES=3
```

---

## Troubleshooting Deployment

### Container won't start
```bash
# Check logs
docker logs dsx-assistant

# Common issues:
# - Missing API key: Set DSX_API_KEY env var
# - Missing dependency: Rebuild image
# - Port in use: Change -p mapping
```

### High memory usage
```bash
# Check container memory
docker stats dsx-assistant

# Solution:
# - Increase container memory limit
# - Reduce concurrent workers
# - Archive old database records
```

### API connection issues
```bash
# Test connectivity from container
docker exec dsx-assistant curl https://openrouter.ai/api/v1/models

# Check API key validity
docker exec dsx-assistant bash -c 'echo $DSX_API_KEY'
```

---

## Production Checklist

- [ ] Use strong, unique API keys (rotate regularly)
- [ ] Enable HTTPS for web access (use reverse proxy)
- [ ] Set resource limits (memory, CPU)
- [ ] Configure health checks
- [ ] Enable logging and monitoring
- [ ] Set up backup for SQLite database
- [ ] Review access control and authentication
- [ ] Test failover and recovery procedures
- [ ] Document runbook for team
- [ ] Plan for scaling (load balancer, horizontal scaling)

