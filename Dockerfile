# ISO Toolkit - Frontend Service
# This Dockerfile builds the React/Vite frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ .

# Build the application with backend URL
ARG VITE_API_URL=https://iso-toolkit.zeabur.app
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/dist /app/dist

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Serve the application
CMD ["sh", "-c", "serve -s dist -l ${PORT:-80}"]
