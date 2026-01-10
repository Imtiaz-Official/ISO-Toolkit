#!/usr/bin/env python
"""
Startup script for ISO Toolkit web application.

Starts both the FastAPI backend and serves the frontend.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def check_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def main():
    """Start the web application."""
    print("=" * 60)
    print("ISO Toolkit Web Application")
    print("=" * 60)
    print()

    # Check if ports are available
    if check_port_in_use(8000):
        print("[yellow]Port 8000 is already in use. Please stop the other process first.[/yellow]")
        print()
        response = input("Try to start anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Start backend
    print("[cyan]Starting FastAPI backend on http://localhost:8000[/cyan]")
    print("[dim]API docs: http://localhost:8000/docs[/dim]")
    print()

    try:
        import uvicorn
        from api.main import app

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n[yellow]Shutting down...[/yellow]")
    except Exception as e:
        print(f"[red]Error starting backend: {e}[/red]")
        print()
        print("[yellow]Make sure dependencies are installed:[/yellow]")
        print("  cd backend && pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
