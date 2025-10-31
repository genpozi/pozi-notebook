# Cloud Platform Deployment Guide

This guide covers deploying Open Notebook on various cloud platforms that support Docker containers and persistent services.

## 🎯 Platform Compatibility

Open Notebook requires:
- ✅ Docker container support
- ✅ Persistent storage for database
- ✅ Background worker processes
- ✅ Multiple exposed ports (5055, 8502)
- ✅ Long-running processes (not serverless)

### ✅ Compatible Platforms

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Railway** | Easy | $5-20/mo | Quick deployment, managed services |
| **Render** | Easy | $7-25/mo | Simple setup, automatic SSL |
| **DigitalOcean** | Medium | $6-40/mo | Full control, predictable pricing |
| **AWS ECS/Fargate** | Hard | Variable | Enterprise, scalability |
| **Google Cloud Run** | Medium | Variable | Pay-per-use, auto-scaling |
| **Self-hosted VPS** | Medium | $5-20/mo | Maximum control, privacy |

### ❌ Incompatible Platforms

- **Vercel** - Serverless only, no persistent services
- **Netlify** - Static sites and serverless functions only
- **GitHub Pages** - Static sites only
- **Cloudflare Pages** - Static sites only

---

## 🚂 Railway Deployment

**Best for**: Quick deployment with minimal configuration

### Prerequisites
- Railway account ([railway.app](https://railway.app))
- GitHub account (for repository connection)

### Step 1: Prepare Your Repository

1. Fork or clone the Open Notebook repository
2. Ensure you have the latest version with authentication support

### Step 2: Deploy on Railway

1. **Create New Project**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Open Notebook repository

2. **Configure Environment Variables**:
   ```env
   # Required
   OPENAI_API_KEY=sk-...
   
   # Database (Railway auto-configures)
   SURREAL_URL=ws://localhost:8000/rpc
   SURREAL_USER=root
   SURREAL_PASSWORD=root
   SURREAL_NAMESPACE=open_notebook
   SURREAL_DATABASE=production
   
   # Optional: Additional AI providers
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=AIzaSy...
   ```

3. **Configure Dockerfile**:
   - Railway will auto-detect `Dockerfile.single`
   - Ensure it's set as the build target

4. **Expose Ports**:
   - Railway will automatically expose port 8502
   - Add port 5055 in the service settings

5. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (5-10 minutes)
   - Railway will provide a public URL

### Step 3: Access Your Instance

- Frontend: `https://your-app.railway.app`
- API: `https://your-app.railway.app/api`

### Railway Tips

- **Persistent Storage**: Railway provides ephemeral storage by default. For production, add a volume:
  ```
  /app/data -> Mount persistent volume
  /mydata -> Mount persistent volume
  ```

- **Custom Domain**: Add your domain in Railway settings
- **Automatic SSL**: Railway provides free SSL certificates
- **Logs**: View real-time logs in the Railway dashboard

---

## 🎨 Render Deployment

**Best for**: Simple setup with automatic SSL and custom domains

### Prerequisites
- Render account ([render.com](https://render.com))
- Docker Hub or GitHub Container Registry

### Step 1: Create Web Service

1. **Go to Render Dashboard**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   ```yaml
   Name: open-notebook
   Environment: Docker
   Region: Choose closest to you
   Branch: main
   Dockerfile Path: Dockerfile.single
   ```

3. **Set Environment Variables**:
   ```env
   OPENAI_API_KEY=sk-...
   SURREAL_URL=ws://localhost:8000/rpc
   SURREAL_USER=root
   SURREAL_PASSWORD=root
   SURREAL_NAMESPACE=open_notebook
   SURREAL_DATABASE=production
   ```

4. **Configure Instance**:
   - Instance Type: Starter ($7/mo) or higher
   - Disk: Add persistent disk for `/app/data` and `/mydata`

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy automatically

### Step 2: Configure Custom Domain (Optional)

1. Go to service settings
2. Add custom domain
3. Update DNS records as instructed
4. Render provides automatic SSL

### Render Tips

- **Health Checks**: Configure at `/api/health`
- **Auto-Deploy**: Enable auto-deploy from GitHub
- **Scaling**: Upgrade instance type for better performance
- **Logs**: Real-time logs in dashboard

---

## 🌊 DigitalOcean App Platform

**Best for**: Predictable pricing and full control

### Prerequisites
- DigitalOcean account ([digitalocean.com](https://digitalocean.com))
- Docker Hub or GitHub Container Registry

### Step 1: Create App

1. **Go to Apps**:
   - Click "Create" → "Apps"
   - Choose "Docker Hub" or "GitHub"

2. **Configure Source**:
   - Repository: `lfnovo/open_notebook`
   - Tag: `v1-latest-single`
   - Or connect GitHub repository

3. **Configure Resources**:
   ```yaml
   Name: open-notebook
   Type: Web Service
   HTTP Port: 8502
   HTTP Routes: /
   ```

4. **Add Environment Variables**:
   ```env
   OPENAI_API_KEY=${OPENAI_API_KEY}
   SURREAL_URL=ws://localhost:8000/rpc
   SURREAL_USER=root
   SURREAL_PASSWORD=root
   SURREAL_NAMESPACE=open_notebook
   SURREAL_DATABASE=production
   ```

5. **Add Persistent Storage**:
   - Mount path: `/app/data`
   - Mount path: `/mydata`

6. **Choose Plan**:
   - Basic: $6/mo (512MB RAM)
   - Professional: $12/mo (1GB RAM) - Recommended

### Step 2: Deploy

1. Review configuration
2. Click "Create Resources"
3. Wait for deployment (5-10 minutes)

### DigitalOcean Tips

- **Managed Database**: Consider using DigitalOcean Managed Database for SurrealDB
- **Monitoring**: Built-in metrics and alerts
- **Scaling**: Easy horizontal and vertical scaling
- **Backups**: Automatic daily backups available

---

## ☁️ AWS ECS/Fargate

**Best for**: Enterprise deployments with advanced requirements

### Prerequisites
- AWS account with ECS access
- AWS CLI configured
- Docker image pushed to ECR

### Step 1: Push Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name open-notebook

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag lfnovo/open_notebook:v1-latest-single YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/open-notebook:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/open-notebook:latest
```

### Step 2: Create ECS Task Definition

```json
{
  "family": "open-notebook",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "open-notebook",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/open-notebook:latest",
      "portMappings": [
        {
          "containerPort": 8502,
          "protocol": "tcp"
        },
        {
          "containerPort": 5055,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "sk-..."
        },
        {
          "name": "SURREAL_URL",
          "value": "ws://localhost:8000/rpc"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "data",
          "containerPath": "/app/data"
        },
        {
          "sourceVolume": "surreal",
          "containerPath": "/mydata"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "data",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxx"
      }
    },
    {
      "name": "surreal",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxx"
      }
    }
  ]
}
```

### Step 3: Create ECS Service

```bash
aws ecs create-service \
  --cluster open-notebook-cluster \
  --service-name open-notebook \
  --task-definition open-notebook \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### Step 4: Configure Load Balancer

1. Create Application Load Balancer
2. Configure target groups for ports 8502 and 5055
3. Add SSL certificate from ACM
4. Update DNS to point to ALB

### AWS Tips

- **EFS**: Use EFS for persistent storage
- **Secrets Manager**: Store API keys securely
- **CloudWatch**: Monitor logs and metrics
- **Auto Scaling**: Configure based on CPU/memory
- **Cost**: Use Fargate Spot for 70% savings

---

## 🏠 Self-Hosted VPS

**Best for**: Maximum control and privacy

### Prerequisites
- VPS with Ubuntu 20.04+ (DigitalOcean, Linode, Vultr, etc.)
- SSH access
- Domain name (optional)

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login for group changes
```

### Step 2: Deploy Open Notebook

```bash
# Create directory
mkdir ~/open-notebook
cd ~/open-notebook

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  open_notebook:
    image: lfnovo/open_notebook:v1-latest-single
    ports:
      - "8502:8502"
      - "5055:5055"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SURREAL_URL=ws://localhost:8000/rpc
      - SURREAL_USER=root
      - SURREAL_PASSWORD=root
      - SURREAL_NAMESPACE=open_notebook
      - SURREAL_DATABASE=production
    volumes:
      - ./data:/app/data
      - ./surreal_data:/mydata
    restart: always
EOF

# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
EOF

# Start services
docker-compose up -d
```

### Step 3: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8502/tcp
sudo ufw allow 5055/tcp
sudo ufw enable
```

### Step 4: Setup Reverse Proxy (Optional)

See [Reverse Proxy Configuration](reverse-proxy.md) for detailed nginx/Caddy setup.

### VPS Tips

- **Backups**: Regular backups of `./data` and `./surreal_data`
- **Updates**: `docker-compose pull && docker-compose up -d`
- **Monitoring**: Install monitoring tools (Netdata, Prometheus)
- **Security**: Keep system updated, use SSH keys, configure fail2ban

---

## 🔒 Security Considerations

### For All Platforms

1. **Environment Variables**:
   - Never commit API keys to Git
   - Use platform secret management
   - Rotate keys regularly

2. **Authentication**:
   - Change default admin password immediately
   - Use strong passwords for all accounts
   - Enable 2FA where available

3. **Network Security**:
   - Use HTTPS/SSL for all connections
   - Configure firewall rules
   - Limit exposed ports

4. **Database Security**:
   - Use strong database passwords
   - Enable database authentication
   - Regular backups

5. **Updates**:
   - Keep Docker images updated
   - Monitor security advisories
   - Test updates in staging first

---

## 📊 Cost Comparison

| Platform | Monthly Cost | Setup Time | Difficulty | Best For |
|----------|-------------|------------|------------|----------|
| Railway | $5-20 | 10 min | Easy | Quick start |
| Render | $7-25 | 15 min | Easy | Production ready |
| DigitalOcean | $6-40 | 20 min | Medium | Predictable costs |
| AWS ECS | $20-100+ | 60 min | Hard | Enterprise |
| VPS | $5-20 | 30 min | Medium | Full control |

**Note**: Costs don't include AI API usage (OpenAI, Anthropic, etc.)

---

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs open-notebook

# Common issues:
# - Missing environment variables
# - Port conflicts
# - Insufficient memory
```

### Can't Access Frontend

```bash
# Check if ports are exposed
docker ps

# Check firewall
sudo ufw status

# Check if service is running
curl http://localhost:8502
```

### Database Connection Issues

```bash
# Check SurrealDB is running
docker exec -it open-notebook ps aux | grep surreal

# Check database files
ls -la ./surreal_data/
```

### Performance Issues

- Increase instance size/memory
- Check AI provider response times
- Monitor CPU/memory usage
- Consider using faster AI providers

---

## 📚 Additional Resources

- [Docker Deployment Guide](docker.md) - Local Docker setup
- [Reverse Proxy Configuration](reverse-proxy.md) - Custom domains and SSL
- [Security Configuration](security.md) - Production security
- [Troubleshooting Guide](../troubleshooting/index.md) - Common issues

---

## 🆘 Getting Help

- **Discord**: [Join our community](https://discord.gg/37XJPXfz2w)
- **GitHub Issues**: [Report bugs](https://github.com/genpozi/pozi-notebook/issues)
- **Documentation**: [Full docs](../index.md)

---

**Ready to deploy?** Choose your platform above and follow the step-by-step guide!
