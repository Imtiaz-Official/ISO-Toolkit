"""
Database session management for ISO Toolkit web application.
Supports PostgreSQL for production (Render) and SQLite for local development.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Generator
import os

from api.database.models import Base


def get_database_url() -> str:
    """
    Get database URL.

    Priority:
    1. DATABASE_URL environment variable (PostgreSQL from Render)
    2. SQLite fallback for local development

    Returns:
        Database URL for SQLAlchemy
    """
    # Check for DATABASE_URL first (Render PostgreSQL)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # Fallback to SQLite for local development
    db_path = Path.home() / ".iso-toolkit" / "downloads.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


# Create engine
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {},
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database tables and create default admin user if needed."""
    from api.database.models import User
    from api.auth.auth_utils import get_password_hash

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create default admin user if it doesn't exist
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "AdminPass123")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash(default_password),
                is_admin=True,
                is_active=True,
                password_changed=False  # Force password change on first login
            )
            db.add(admin_user)
            db.commit()
            print("=" * 60)
            print("DEFAULT ADMIN USER CREATED")
            print("=" * 60)
            print(f"Username: admin")
            print(f"Password: {default_password}")
            print("SECURITY WARNING: Change this password immediately!")
            print("=" * 60)
        else:
            print("Database initialized. Admin user exists.")
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()


def get_session() -> Generator[Session, None, None]:
    """
    Get database session.

    Yields:
        Database session

    Usage:
        with get_session() as session:
            session.query(DownloadRecord).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.

    Yields:
        Database session

    Usage:
        @app.get("/downloads")
        def get_downloads(db: Session = Depends(get_db)):
            return db.query(DownloadRecord).all()
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
