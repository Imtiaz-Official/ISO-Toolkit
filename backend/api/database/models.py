"""
SQLAlchemy database models for ISO Toolkit web application.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, Text, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Import enums from core to avoid duplication
from core.models import DownloadState

Base = declarative_base()


class ISOOverride(Base):
    """
    Database model for custom ISO entries and built-in ISO overrides.
    Admins can add custom ISOs or override built-in ISO URLs.
    """
    __tablename__ = "iso_overrides"

    id = Column(Integer, primary_key=True, index=True)
    # ISO identifier (matches the built-in ID format: category_name_version_arch)
    iso_id = Column(String(255), unique=True, nullable=False, index=True)

    # ISO Information
    name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    architecture = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)

    # Download Details
    url = Column(String(2048), nullable=False)
    size = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)

    # Checksum
    checksum = Column(String(255), nullable=True)
    checksum_type = Column(String(50), nullable=True)

    # Metadata
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.iso_id,
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "architecture": self.architecture,
            "language": self.language,
            "url": self.url,
            "size": self.size or 0,
            "description": self.description,
            "icon": self.icon,
            "checksum": self.checksum,
            "checksum_type": self.checksum_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_custom": True,
            "is_enabled": self.is_enabled,
            "can_edit": True
        }


class User(Base):
    """
    User model for admin authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    password_changed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "password_changed": self.password_changed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class DownloadRecord(Base):
    """
    Database record for downloads.
    Persists download state across server restarts.
    """
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    # OS Information
    os_name = Column(String, nullable=False)
    os_version = Column(String, nullable=False)
    os_category = Column(String, nullable=False)
    os_architecture = Column(String, nullable=False)
    os_language = Column(String, nullable=False)
    # Download Details
    url = Column(String, nullable=False)
    output_path = Column(String, nullable=False)
    # State - use String for PostgreSQL compatibility (validated at app level)
    state = Column(String, default=DownloadState.PENDING.value, nullable=False)
    # Progress
    progress = Column(Float, default=0.0)
    downloaded_bytes = Column(BigInteger, default=0)
    total_bytes = Column(BigInteger, default=0)
    speed = Column(Float, default=0.0)
    eta = Column(Integer, default=0)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    # Error
    error_message = Column(Text, nullable=True)
    # Checksum
    checksum = Column(String, nullable=True)
    checksum_type = Column(String, nullable=True)
    checksum_verified = Column(Integer, default=0)  # 0=not checked, 1=passed, -1=failed

    @property
    def state_enum(self) -> DownloadState:
        """Get state as DownloadState enum."""
        return DownloadState(self.state)

    @state_enum.setter
    def state_enum(self, value: DownloadState):
        """Set state from DownloadState enum."""
        self.state = value.value

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "os_category": self.os_category,
            "os_architecture": self.os_architecture,
            "os_language": self.os_language,
            "url": self.url,
            "output_path": self.output_path,
            "state": self.state,
            "progress": self.progress,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "speed": self.speed,
            "eta": self.eta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "checksum": self.checksum,
            "checksum_verified": self.checksum_verified,
        }


class Settings(Base):
    """
    User settings stored in database.
    """
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
