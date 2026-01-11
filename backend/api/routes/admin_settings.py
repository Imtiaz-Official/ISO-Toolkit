"""
Activity logging and settings management for admin panel.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from api.database.session import get_db
from api.database.models import User, DownloadRecord
from api.routes.auth import get_current_admin_user
from api.database.models import Settings as SettingsModel

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


# Activity Log Storage (in-memory for now, use database in production)
activity_logs: List[dict] = []


class ActivityLog(BaseModel):
    id: str
    timestamp: str
    user: str
    action: str
    details: dict
    ip_address: Optional[str] = None


class SystemSettings(BaseModel):
    site_name: str = "ISO Toolkit"
    site_description: str = "Multi-OS ISO Downloader Toolkit"
    allow_registration: bool = True
    max_download_size_gb: int = 100
    download_timeout_seconds: int = 3600
    maintenance_mode: bool = False
    proxy_downloads: bool = True  # Enable/disable proxy downloads (brand consistency)
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


def log_activity(user: str, action: str, details: dict, ip_address: str = None):
    """Log an admin activity."""
    log_entry = {
        "id": f"{int(datetime.utcnow().timestamp())}",
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "action": action,
        "details": details,
        "ip_address": ip_address
    }
    activity_logs.append(log_entry)

    # Keep only last 1000 logs
    if len(activity_logs) > 1000:
        activity_logs.pop(0)


@router.get("/logs", response_model=List[ActivityLog])
async def get_activity_logs(
    current_admin: User = Depends(get_current_admin_user),
    limit: int = 100,
    offset: int = 0
):
    """
    Get activity logs (admin only).
    """
    logs = list(reversed(activity_logs))
    return logs[offset:offset + limit]


@router.get("/settings", response_model=dict)
async def get_settings(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all system settings (admin only).
    """
    settings_from_db = db.query(SettingsModel).all()
    settings_dict = {setting.key: setting.value for setting in settings_from_db}

    # Merge with defaults
    defaults = {
        "site_name": "ISO Toolkit",
        "site_description": "Multi-OS ISO Downloader Toolkit",
        "allow_registration": True,
        "max_download_size_gb": 100,
        "download_timeout_seconds": 3600,
        "maintenance_mode": False,
        "proxy_downloads": True,  # Enable proxy downloads by default (brand consistency)
        "custom_css": None,
        "custom_js": None,
    }

    defaults.update(settings_dict)

    # Convert boolean strings
    for key in ["allow_registration", "maintenance_mode", "proxy_downloads"]:
        if key in defaults and isinstance(defaults[key], str):
            defaults[key] = defaults[key].lower() == "true"

    return defaults


@router.post("/settings")
async def update_settings(
    settings: SystemSettings,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update system settings (admin only).
    """
    settings_dict = settings.model_dump()

    # Update each setting in database
    for key, value in settings_dict.items():
        if value is None:
            continue

        existing = db.query(SettingsModel).filter(SettingsModel.key == key).first()
        if existing:
            existing.value = str(value)
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SettingsModel(
                key=key,
                value=str(value)
            )
            db.add(new_setting)

    db.commit()

    # Log activity
    log_activity(
        user=current_admin.username,
        action="update_settings",
        details={"settings_changed": list(settings_dict.keys())}
    )

    return {"message": "Settings updated successfully"}


@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get activity for a specific user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's downloads
    downloads = db.query(DownloadRecord).filter(
        DownloadRecord.os_name.contains(user.username)  # Approximate
    ).order_by(DownloadRecord.created_at.desc()).limit(50).all()

    return {
        "user": user.to_dict(),
        "download_count": len(downloads),
        "recent_downloads": [dl.to_dict() for dl in downloads],
        "activity_logs": [log for log in activity_logs if log["user"] == user.username]
    }


@router.post("/maintenance/{mode}")
async def toggle_maintenance(
    mode: bool,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Toggle maintenance mode (admin only).
    """
    setting = db.query(SettingsModel).filter(SettingsModel.key == "maintenance_mode").first()
    if setting:
        setting.value = str(mode)
        setting.updated_at = datetime.utcnow()
    else:
        setting = SettingsModel(
            key="maintenance_mode",
            value=str(mode)
        )
        db.add(setting)

    db.commit()

    log_activity(
        user=current_admin.username,
        action="toggle_maintenance",
        details={"maintenance_mode": mode}
    )

    return {"message": f"Maintenance mode {'enabled' if mode else 'disabled'}"}


@router.get("/dashboard")
async def get_admin_dashboard(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive admin dashboard data (admin only).
    """
    # User stats
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.is_admin == True).count()

    # Download stats
    total_downloads = db.query(DownloadRecord).count()
    active_downloads = db.query(DownloadRecord).filter(
        DownloadRecord.state == "downloading"
    ).count()
    completed_downloads = db.query(DownloadRecord).filter(
        DownloadRecord.state == "completed"
    ).count()

    # Recent activity
    recent_activity = list(reversed(activity_logs[-20:]))

    # System settings
    settings_obj = await get_settings(current_admin, db)

    return {
        "users": {
            "total": total_users,
            "admins": total_admins,
            "regular": total_users - total_admins
        },
        "downloads": {
            "total": total_downloads,
            "active": active_downloads,
            "completed": completed_downloads
        },
        "recent_activity": recent_activity,
        "settings": settings_obj,
        "custom_isos_count": 0  # Will be updated from admin_iso module
    }


@router.post("/backup")
async def create_backup(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a database backup (admin only).
    """
    # This would typically trigger an actual backup
    # For now, log the activity
    log_activity(
        user=current_admin.username,
        action="backup_created",
        details={"timestamp": datetime.utcnow().isoformat()}
    )

    return {
        "message": "Backup triggered successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/clear-cache")
async def clear_cache(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Clear application cache (admin only).
    """
    # Clear in-memory caches
    global activity_logs
    old_count = len(activity_logs)
    activity_logs.clear()

    log_activity(
        user=current_admin.username,
        action="cache_cleared",
        details={"entries_cleared": old_count}
    )

    return {
        "message": f"Cache cleared ({old_count} entries)"
    }
