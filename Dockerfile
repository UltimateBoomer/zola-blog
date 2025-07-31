# Multi-stage build: Build the Zola site first
FROM ghcr.io/getzola/zola:v0.21.0 as builder

# Copy the source code
COPY . /app
WORKDIR /app

# Build the site
RUN zola build

# Production stage: Serve with nginx
FROM nginx:alpine

# Copy the built site from the builder stage
COPY --from=builder /app/public /usr/share/nginx/html

# Use default nginx configuration optimized for static sites

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
