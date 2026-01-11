# ISO Toolkit Web Application

<div align="center">

![ISO Toolkit](https://img.shields.io/badge/ISO_Toolkit-v1.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**A beautiful, full-stack web application for browsing and downloading Windows, Linux, macOS, and BSD ISO images with real-time progress tracking.**

[Live Demo](https://iso-toolkit.onrender.com) • [Features](#features) • [Installation](#installation) • [Deployment](#deployment)

</div>

---

## ✨ Features

### 🖥️ OS Browsing
- **110+ Linux Distributions** - Ubuntu, Fedora, Debian, Arch, Manjaro, Alpine, Raspberry Pi OS, and many more
- **Windows Versions** - Windows 11, 10, 8.1, 7, XP with multiple editions
- **macOS** - Latest releases from Sequoia to El Capitan
- **BSD** - FreeBSD, OpenBSD, NetBSD
- **ARM/Single Board Computers** - Raspberry Pi OS, LibreELEC, DietPi
- **Subcategory Filtering** - Browse by distro family (Ubuntu, Fedora, Arch, etc.) or Windows version
- **Smart Search** - Search by name, version, or description
- **Official Logos** - High-quality SVG logos from official distro sources

### ⬇️ Download Management
- **Proxy Downloads** - All downloads proxied through your domain for brand consistency
- **Real-time Progress** - WebSocket updates for speed, ETA, progress percentage
- **Download Controls** - Start, pause, resume, cancel downloads
- **Checksum Verification** - Automatic SHA256/MD5 verification
- **Download History** - Track all past and current downloads
- **Concurrent Downloads** - Manage multiple downloads simultaneously

### 🔐 Admin Panel
- **Authentication** - Secure admin login with JWT tokens
- **ISO Management** - Add, edit, delete custom ISO entries
- **Override Built-ins** - Override any built-in ISO with custom data
- **Category Filtering** - Filter by Windows, Linux, macOS, BSD
- **User Management** - View and manage user accounts
- **Activity Logs** - Track all admin actions
- **Analytics Dashboard** - Download statistics and system metrics
- **Settings Management** - Configure global app settings

### 🎨 User Experience
- **Responsive Design** - Works perfectly on mobile, tablet, and desktop
- **Dark/Light Theme** - Toggle between themes with auto-detection
- **Modern UI** - Clean, intuitive interface with smooth animations
- **URL State Persistence** - Share links, browser back/button support
- **Persistent State** - Remembers your selections across page refreshes

---

## 🛠️ Tech Stack

### Backend
- **FastAPI 0.115** - Modern async Python web framework
- **PostgreSQL** - Production database (Render.com free tier)
- **SQLite** - Local development database
- **SQLAlchemy 2.0** - ORM with async support
- **WebSocket** - Real-time download progress updates
- **Pydantic 2.9** - Data validation and serialization
- **httpx** - Async HTTP client for proxy downloads
- **python-jose** - JWT authentication

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript 5** - Type-safe development
- **Vite 6** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Router** - Client-side routing with URL state

### DevOps
- **Render.com** - Production deployment
- **GitHub Actions** - CI/CD ready
- **Docker** - Container support (optional)

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **pip** and **npm**

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

---

## 🚀 Running the Application

### Development Mode

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
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Production Build

**Backend:**
```bash
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Static files will be in frontend/dist
```

---

## 🌐 Deployment

### Render.com (Recommended)

1. **Push your code to GitHub**
2. **Create account at [Render.com](https://render.com)**
3. **Create a new Web Service**
4. **Connect your GitHub repository**
5. **Configure build settings:**

```
Build Command: cd frontend && npm install && npm run build
Start Command: cd backend && uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

6. **Add Environment Variables:**

```
DATABASE_URL=postgresql://...
DEFAULT_ADMIN_PASSWORD=your_secure_password
ALLOWED_ORIGINS=https://your-domain.onrender.com
```

7. **Create PostgreSQL Database** (Free tier available)
8. **Deploy!**

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions including:
- Nginx configuration
- SSL/TLS setup
- Systemd service files
- Reverse proxy setup

---

## 📁 Project Structure

```
iso-toolkit/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   ├── main.py            # FastAPI app & routes
│   │   ├── routes/            # API endpoints
│   │   │   ├── os.py          # OS browsing
│   │   │   ├── downloads.py   # Download management
│   │   │   ├── ws.py          # WebSocket handler
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── admin_iso.py   # Admin ISO management
│   │   │   ├── admin_settings.py
│   │   │   ├── analytics.py   # Statistics
│   │   │   └── proxy_download.py  # Proxy downloads
│   │   ├── database/          # SQLAlchemy models & session
│   │   ├── models/            # Pydantic schemas
│   │   └── auth/              # Authentication utilities
│   └── core/                  # Shared core logic
│       ├── os/                # OS providers
│       │   ├── base.py        # Base provider & registry
│       │   ├── windows.py     # Windows provider
│       │   ├── linux.py       # Linux provider (110+ distros)
│       │   ├── macos.py       # macOS provider
│       │   └── bsd.py         # BSD provider
│       └── models.py          # Core data models
├── frontend/                   # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── BrowseOS.tsx   # OS browsing with subcategories
│   │   │   ├── Downloads.tsx  # Download manager
│   │   │   ├── Settings.tsx   # User settings
│   │   │   ├── Login.tsx
│   │   │   ├── ChangePassword.tsx
│   │   │   └── AdminDashboard.tsx  # Admin panel
│   │   ├── components/        # Reusable components
│   │   │   └── LogoImage.tsx  # Distro logo component
│   │   ├── services/          # API client
│   │   ├── contexts/          # Auth context
│   │   ├── hooks/             # useWebSocket hook
│   │   ├── assets/            # Static assets, logos
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── py/                        # Legacy TUI (deprecated)
├── rust/                      # Rust extension (optional)
└── README.md
```

---

## 🔌 API Endpoints

### OS Endpoints
- `GET /api/os/categories` - List OS categories with counts
- `GET /api/os/linux/subcategories` - List Linux distributions
- `GET /api/os/windows/subcategories` - List Windows versions
- `GET /api/os/{category}` - List OS for category (Windows, Linux, macOS, BSD)
- `GET /api/os/{category}?subcategory={name}` - Filter by subcategory
- `GET /api/os/search?query={query}` - Search OS

### Download Endpoints
- `POST /api/downloads/start` - Start a download
- `GET /api/downloads` - List all downloads
- `GET /api/downloads/{id}` - Get download status
- `POST /api/downloads/{id}/pause` - Pause download
- `POST /api/downloads/{id}/resume` - Resume download
- `DELETE /api/downloads/{id}` - Cancel download
- `GET /api/downloads/stats` - Get statistics

### Proxy Download Endpoints
- `GET /download/{id}` - Proxy download by database ID
- `GET /download/direct/{category}/{name}` - Direct ISO download
- `GET /download/url/{base64_url}` - Proxy any URL

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

### Admin Endpoints
- `GET /api/admin/iso` - List all ISOs (built-in + custom)
- `POST /api/admin/iso` - Add custom ISO
- `PUT /api/admin/iso/{id}` - Update ISO
- `DELETE /api/admin/iso/{id}` - Delete ISO
- `GET /api/admin/stats` - Admin statistics
- `GET /api/admin/logs` - Activity logs
- `GET /api/admin/settings` - Global settings
- `PUT /api/admin/settings` - Update settings

### WebSocket
- `WS /api/ws/downloads` - Real-time download progress updates

---

## ⚙️ Environment Variables

### Backend (.env)
```bash
# Database (PostgreSQL for production, SQLite for local)
DATABASE_URL=postgresql://user:pass@host:port/database

# Admin Credentials
DEFAULT_ADMIN_PASSWORD=your_secure_password

# CORS (optional)
ALLOWED_ORIGINS=https://your-domain.com,https://another-domain.com
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api/ws/downloads
```

---

## 🐧 Supported Linux Distributions (110+)

**Ubuntu Family:** Ubuntu, Kubuntu, Xubuntu, Lubuntu, Pop!_OS, Linux Mint, elementary OS, Zorin OS, KDE neon, Ubuntu MATE, Ubuntu Studio, Ubuntu Budgie, Ubuntu Cinnamon, Edubuntu

**Fedora & RHEL Family:** Fedora, Fedora Workstation, Fedora KDE, Fedora XFCE, Fedora Server, Fedora Cinnamon, Fedora LXQt, Fedora ARM, Rocky Linux, AlmaLinux, CentOS Stream, RHEL, Oracle Linux

**Debian Family:** Debian, Raspberry Pi OS

**Arch Family:** Arch Linux, Manjaro, EndeavourOS, Garuda Linux, Artix Linux, ArcoLinux

**Major Independent:** openSUSE, Solus, NixOS, deepin, MX Linux, antiX, Void Linux, Gentoo, Slackware

**Security/Privacy:** Kali Linux, Parrot OS, Tails

**Lightweight/Minimal:** Alpine Linux, Puppy Linux, Bodhi Linux, Q4OS, PCLinuxOS, DietPi, Clear Linux, Mageia

**ARM/SBC:** Raspberry Pi OS, LibreELEC, Fedora ARM, Ubuntu MATE ARM

**Cloud/Enterprise:** Amazon Linux

**Others:** BigLinux, RebeccaBlackOS

---

## 🔒 Default Admin Credentials

After first deployment, login with:
- **Username:** `admin`
- **Password:** Check your deployment logs or set `DEFAULT_ADMIN_PASSWORD` environment variable

⚠️ **IMPORTANT:** Change the password immediately after first login!

---

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions, please open a [GitHub Issue](https://github.com/Imtiaz-Official/ISO-Toolkit/issues).

---

<div align="center">

**Made with ❤️ by the ISO Toolkit team**

[⭐ Star us on GitHub](https://github.com/Imtiaz-Official/ISO-Toolkit) • [🐦 Follow us](https://twitter.com) • [💬 Discord](https://discord.gg)

</div>
