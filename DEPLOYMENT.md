# Zeabur Deployment Guide

This guide explains how to deploy the ISO Toolkit to Zeabur.

## Prerequisites

1. A GitHub account with the code pushed to a repository
2. A Zeabur account (sign up at https://zeabur.com)
3. Zeabur CLI (optional) or use the web dashboard

## Quick Start (Web Dashboard)

### 1. Connect Your Repository

1. Log in to [Zeabur](https://zeabur.com)
2. Click "New Project"
3. Select "Import from GitHub"
4. Authorize Zeabur to access your repository
5. Select the `ISO-Toolkit` repository

### 2. Deploy Backend

1. Click "Add Service"
2. Select "Docker"
3. Zeabur will detect the `Dockerfile.backend`
4. Configure:
   - **Service Name**: `backend`
   - **Environment Variables**:
     ```
     PORT=8000
     ALLOWED_ORIGINS=https://your-frontend-domain.zeabur.app
     ```
5. Click "Deploy"

### 3. Deploy Frontend

1. Click "Add Service" again
2. Select "Docker"
3. Zeabur will detect the `Dockerfile.frontend`
4. Configure:
   - **Service Name**: `frontend`
5. Click "Deploy"

### 4. Configure Networking

1. Once both services are deployed, note the backend URL
2. Update the frontend service's environment variable:
   - `VITE_API_URL` should point to backend URL or `/api` for proxy
3. Generate a custom domain for the frontend (optional)

## Environment Variables

### Backend (PORT=8000)
- `PORT`: Port for the FastAPI server (default: 8000)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend URLs

### Frontend
- `VITE_API_URL`: API base URL (default: `/api` for nginx proxy)

## Volumes

The backend service uses a persistent volume for downloads:
- Path: `/app/downloads`
- This ensures downloaded ISOs persist across deployments

## Health Checks

Both services include health checks:
- Backend: `GET /health`
- Frontend: HTTP check on port 80

## Troubleshooting

### Build Failures
- Check Dockerfile syntax
- Verify all dependencies are in requirements.txt
- Ensure Node.js version is compatible (20.x)

### CORS Errors
- Add your frontend domain to `ALLOWED_ORIGINS`
- Separate multiple origins with commas

### WebSocket Connection Issues
- Ensure nginx proxy is configured for WebSocket upgrades
- Check that backend WebSocket port is accessible

## Free Tier Limitations

Zeabur's free tier includes:
- ✅ Always running (no spin-down)
- ✅ Sufficient bandwidth for testing
- ✅ Persistent storage
- ⚠️ Limited CPU/RAM (may be slow for large downloads)

## Alternative: Manual Deploy with CLI

```bash
# Install Zeabur CLI
npm install -g @zeabur/cli

# Login
zeabur login

# Create project
zeabur init

# Deploy
zeabur deploy
```

## Next Steps

1. Set up a custom domain (optional)
2. Configure SSL (automatic on Zeabur)
3. Monitor logs in Zeabur dashboard
4. Set up alerts for downtime
