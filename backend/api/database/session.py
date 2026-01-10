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


def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


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
