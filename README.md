# ISO Toolkit Web Application

A beautiful, full-stack web application for downloading Windows and Linux ISO images with real-time progress tracking.

## Features

- **Browse OS by Category**: Windows, Linux, macOS, BSD
- **Real-time Progress**: WebSocket updates for download speed, ETA, progress %
- **Download Management**: Start, pause, resume, cancel downloads
- **Checksum Verification**: Automatic SHA256/MD5 verification
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Dark/Light Theme**: Toggle between themes

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **WebSocket** - Real-time download progress updates
- **SQLite + SQLAlchemy** - Database for persistence
- **Pydantic** - Data validation and serialization

### Frontend
- **React 18 + TypeScript** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **Axios** - HTTP client

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- pip and npm

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Development (Separate Servers)

**Terminal 1 - Start Backend:**
```bash
cd backend
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Then visit:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Using the Startup Script

```bash
python start_web.py
```

This will start the FastAPI backend on http://127.0.0.1:8000

Then in a separate terminal:
```bash
cd frontend
npm run dev
```

## Building for Production

### Backend
```bash
# No build needed, just run:
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Static files will be in frontend/dist
```

Serve the built frontend with nginx, caddy, or any web server.

## API Endpoints

### OS Endpoints
- `GET /api/os/categories` - List OS categories
- `GET /api/os/{category}` - List OS for category
- `GET /api/os/search?query={query}` - Search OS

### Download Endpoints
- `POST /api/downloads/start` - Start a download
- `GET /api/downloads` - List all downloads
- `GET /api/downloads/{id}` - Get download status
- `POST /api/downloads/{id}/pause` - Pause download
- `POST /api/downloads/{id}/resume` - Resume download
- `DELETE /api/downloads/{id}` - Cancel download
- `DELETE /api/downloads/completed` - Clear completed downloads
- `GET /api/downloads/stats` - Get statistics

### WebSocket
- `WS /api/ws/downloads` - Real-time download progress

## Project Structure

```
iso-toolkit/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   ├── main.py            # FastAPI app
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # WebSocket manager, download service
│   │   ├── database/          # SQLAlchemy models
│   │   └── models/            # Pydantic schemas
│   └── core/                  # Shared core logic
├── frontend/                   # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── hooks/             # useWebSocket hook
│   │   └── types/             # TypeScript types
│   └── package.json
├── py/                        # Legacy TUI (deprecated)
└── rust/                      # Rust extension (optional)
```

## Environment Variables

### Backend (.env)
```
DATABASE_PATH=sqlite:///path/to/database.db
DOWNLOAD_DIR=/path/to/downloads
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api/ws/downloads
```

## Docker Deployment (Optional)

```bash
# Build and run with Docker
docker-compose up --build
```

## Zeabur Deployment (Free Hosting)

This project is configured for deployment on [Zeabur](https://zeabur.com) with a free tier that doesn't spin down.

### Quick Deploy

1. Push your code to GitHub
2. Create an account at [Zeabur](https://zeabur.com)
3. Create a new project and import your repository
4. Zeabur will detect the `zeabur.yaml` configuration and deploy both services

### Deployment Files

- `Dockerfile.backend` - Backend container
- `Dockerfile.frontend` - Frontend container
- `nginx.conf` - Nginx configuration for frontend
- `zeabur.yaml` - Zeabur deployment configuration
- `.dockerignore` - Files to exclude from Docker builds

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Features

### Browse OS
- Windows (11, 10, 8.1, 7, XP)
- Linux (Ubuntu, Fedora, Debian, Mint, Arch, and more)
- macOS
- BSD

### Download Manager
- Real-time progress tracking via WebSocket
- Pause, resume, cancel downloads
- Checksum verification (SHA256)
- Download history and statistics

### Settings & Appearance
- Theme: Light, Dark, Auto
- Accent color customization
- Font size adjustment
- Compact mode
- Show/hide file sizes
- Language & Region settings

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
