# Multi-stage build: Build the Zola site first
FROM docker.io/alpine:3.18 as builder

# Install dependencies
RUN apk add --no-cache curl ca-certificates

# Install Zola - detect architecture and download appropriate binary
RUN set -e && \
    ARCH=$(uname -m) && \
    echo "Detected architecture: $ARCH" && \
    case "$ARCH" in \
        x86_64) ZOLA_ARCH="x86_64-unknown-linux-musl" ;; \
        aarch64) ZOLA_ARCH="aarch64-unknown-linux-gnu" ;; \
        *) echo "Unsupported architecture: $ARCH" && exit 1 ;; \
    esac && \
    echo "Downloading Zola for: $ZOLA_ARCH" && \
    curl -fsSL "https://github.com/getzola/zola/releases/download/v0.21.0/zola-v0.21.0-${ZOLA_ARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/zola && \
    echo "Zola installation completed" && \
    /usr/local/bin/zola --version

# Set working directory
WORKDIR /app

# Copy the source code (including theme submodules)
# Note: Ensure git submodules are checked out before building the container
COPY . .

# Build the site
RUN zola build

# Production stage: Serve with nginx
FROM docker.io/nginx:alpine

# Copy the built site from the builder stage
COPY --from=builder /app/public /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Install curl for health check
RUN apk add --no-cache curl

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
