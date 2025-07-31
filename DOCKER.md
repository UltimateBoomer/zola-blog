# Docker Deployment Guide

This guide explains how to build and deploy the Zola blog using Docker containers.

## Quick Start

### Using Pre-built Images from GHCR

The easiest way to run the site is using the pre-built container images:

```bash
# Pull and run the latest version
docker run -d -p 8080:80 --name zola-blog ghcr.io/ultimateboomer/zola-blog:latest

# Visit http://localhost:8080
```

### Building Locally

If you prefer to build the container yourself:

```bash
# Build the container
docker build -t zola-blog .

# Run the container
docker run -d -p 8080:80 --name zola-blog zola-blog

# Visit http://localhost:8080
```

## Container Features

- **Multi-stage build**: Optimized for minimal final image size
- **Multi-architecture**: Supports both AMD64 and ARM64 platforms
- **Alpine Linux**: Lightweight base image for production
- **Nginx**: High-performance web server for static content
- **Health checks**: Built-in health monitoring
- **Cache optimization**: Docker layer caching for faster builds

## Available Tags

The GitHub workflow automatically creates the following tags:

- `latest` - Latest build from the main branch
- `main` - Same as latest
- `v1.0.0` - Specific version tags (when you create releases)
- `1.0` - Major.minor version tags
- `pr-123` - Pull request builds (for testing)

## Docker Compose

For easier management, you can use Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'

services:
  zola-blog:
    image: ghcr.io/ultimateboomer/zola-blog:latest
    ports:
      - "8080:80"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run with:
```bash
docker-compose up -d
```

## Production Deployment

### Environment Variables

The container doesn't require any environment variables, but you can customize nginx behavior:

```bash
docker run -d \
  -p 80:80 \
  --name zola-blog \
  --restart unless-stopped \
  ghcr.io/ultimateboomer/zola-blog:latest
```

### Reverse Proxy Setup

For production with SSL, use a reverse proxy like Traefik or nginx:

#### Traefik Example

```yaml
services:
  zola-blog:
    image: ghcr.io/ultimateboomer/zola-blog:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.blog.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.blog.tls.certresolver=letsencrypt"
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zola-blog
spec:
  replicas: 2
  selector:
    matchLabels:
      app: zola-blog
  template:
    metadata:
      labels:
        app: zola-blog
    spec:
      containers:
      - name: zola-blog
        image: ghcr.io/ultimateboomer/zola-blog:latest
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: zola-blog-service
spec:
  selector:
    app: zola-blog
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

## Troubleshooting

### Container Won't Start

1. Check logs:
   ```bash
   docker logs zola-blog
   ```

2. Verify the container is healthy:
   ```bash
   docker inspect zola-blog | grep -A 5 Health
   ```

### Build Failures

1. Ensure git submodules are initialized:
   ```bash
   git submodule update --init --recursive
   ```

2. Check Docker build logs for specific errors:
   ```bash
   docker build --no-cache -t zola-blog .
   ```

### Theme Issues

If the theme isn't loading correctly, ensure the `themes/linkita` directory contains the theme files:

```bash
ls -la themes/linkita/
```

### Performance Tuning

For high-traffic sites, consider:

1. Using a CDN for static assets
2. Implementing HTTP/2 and gzip compression
3. Adding cache headers for static content
4. Running multiple container replicas behind a load balancer

## Security Considerations

- The container runs nginx as a non-root user
- No sensitive data is included in the image
- Regular base image updates via automated builds
- Health checks prevent serving broken content

## Updating

To update to the latest version:

```bash
# Pull the latest image
docker pull ghcr.io/ultimateboomer/zola-blog:latest

# Stop and remove the old container
docker stop zola-blog
docker rm zola-blog

# Start with the new image
docker run -d -p 8080:80 --name zola-blog ghcr.io/ultimateboomer/zola-blog:latest
```

Or use Docker Compose:

```bash
docker-compose pull
docker-compose up -d
```
