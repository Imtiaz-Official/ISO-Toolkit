"""
Database session management for ISO Toolkit web application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Generator

from api.database.models import Base


# Default database path
DEFAULT_DB_PATH = Path.home() / ".iso-toolkit" / "downloads.db"


def get_database_url(db_path: str | None = None) -> str:
    """
    Get SQLite database URL.

    Args:
        db_path: Custom database path (optional)

    Returns:
        SQLite database URL
    """
    if db_path:
        return f"sqlite:///{db_path}"
    # Ensure directory exists
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH}"


# Create engine
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Export database URL for use in scripts
DATABASE_URL = get_database_url()


def init_database():
    """Initialize database tables and create default admin user if needed."""
    from api.database.models import User
    from api.auth.auth_utils import get_password_hash
    import os

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
            print("Default admin user created successfully - PLEASE CHANGE THE PASSWORD IMMEDIATELY!")
            print(f"Username: admin")
            print(f"Default Password: {default_password}")
            print("SECURITY WARNING: Change this password immediately after first login!")
    except Exception as e:
        db.rollback()
        print(f"Error creating default admin user: {e}")
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
