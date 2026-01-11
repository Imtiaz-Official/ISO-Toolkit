"""
Analytics routes for admin dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel

from api.database.session import get_db
from api.database.models import DownloadRecord, DownloadState, User
from api.routes.auth import get_current_admin_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


class CategoryStats(BaseModel):
    category: str
    count: int
    total_bytes: int


class ArchitectureStats(BaseModel):
    architecture: str
    count: int


class TimeSeriesData(BaseModel):
    date: str
    count: int
    total_bytes: int


class SystemHealth(BaseModel):
    disk_usage_percent: float
    disk_free_gb: float
    disk_total_gb: float
    memory_usage_percent: float
    uptime_seconds: float


class DetailedAnalytics(BaseModel):
    total_downloads: int
    active_downloads: int
    completed_downloads: int
    failed_downloads: int
    total_bytes: int
    category_breakdown: List[CategoryStats]
    architecture_breakdown: List[ArchitectureStats]
    recent_downloads: List[Dict[str, Any]]
    time_series_last_7_days: List[TimeSeriesData]
    top_downloaded_os: List[Dict[str, Any]]


@router.get("/detailed", response_model=DetailedAnalytics)
async def get_detailed_analytics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for admin dashboard.
    """
    # Basic stats
    total = db.query(DownloadRecord).count()
    active = db.query(DownloadRecord).filter(DownloadRecord.state == DownloadState.DOWNLOADING.value).count()
    completed = db.query(DownloadRecord).filter(DownloadRecord.state == DownloadState.COMPLETED.value).count()
    failed = db.query(DownloadRecord).filter(DownloadRecord.state == DownloadState.FAILED.value).count()

    # Total bytes
    total_bytes = db.query(func.sum(DownloadRecord.total_bytes)).filter(
        DownloadRecord.state == DownloadState.COMPLETED.value
    ).scalar() or 0

    # Category breakdown
    category_stats = db.query(
        DownloadRecord.os_category,
        func.count(DownloadRecord.id).label('count'),
        func.sum(DownloadRecord.total_bytes).label('total_bytes')
    ).filter(
        DownloadRecord.state == DownloadState.COMPLETED.value
    ).group_by(DownloadRecord.os_category).all()

    category_breakdown = [
        CategoryStats(category=cat, count=count, total_bytes=bytes_val or 0)
        for cat, count, bytes_val in category_stats
    ]

    # Architecture breakdown
    arch_stats = db.query(
        DownloadRecord.os_architecture,
        func.count(DownloadRecord.id).label('count')
    ).filter(
        DownloadRecord.state == DownloadState.COMPLETED.value
    ).group_by(DownloadRecord.os_architecture).all()

    architecture_breakdown = [
        ArchitectureStats(architecture=arch, count=count)
        for arch, count in arch_stats
    ]

    # Recent downloads
    recent_downloads = db.query(DownloadRecord).order_by(
        desc(DownloadRecord.created_at)
    ).limit(10).all()

    recent_downloads_data = [
        {
            "id": r.id,
            "os_name": r.os_name,
            "os_version": r.os_version,
            "os_category": r.os_category,
            "state": r.state,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_downloads
    ]

    # Time series data for last 7 days
    time_series = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        daily_downloads = db.query(DownloadRecord).filter(
            DownloadRecord.created_at >= date_start,
            DownloadRecord.created_at <= date_end,
            DownloadRecord.state == DownloadState.COMPLETED.value
        ).all()

        time_series.append(TimeSeriesData(
            date=date_start.strftime("%Y-%m-%d"),
            count=len(daily_downloads),
            total_bytes=sum(r.total_bytes or 0 for r in daily_downloads)
        ))

    time_series.reverse()

    # Top downloaded OS
    top_os = db.query(
        DownloadRecord.os_name,
        DownloadRecord.os_version,
        func.count(DownloadRecord.id).label('count')
    ).filter(
        DownloadRecord.state == DownloadState.COMPLETED.value
    ).group_by(
        DownloadRecord.os_name,
        DownloadRecord.os_version
    ).order_by(desc('count')).limit(5).all()

    top_downloaded_os = [
        {"name": name, "version": version, "count": count}
        for name, version, count in top_os
    ]

    return DetailedAnalytics(
        total_downloads=total,
        active_downloads=active,
        completed_downloads=completed,
        failed_downloads=failed,
        total_bytes=total_bytes,
        category_breakdown=category_breakdown,
        architecture_breakdown=architecture_breakdown,
        recent_downloads=recent_downloads_data,
        time_series_last_7_days=time_series,
        top_downloaded_os=top_downloaded_os,
    )


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system health metrics.
    """
    import shutil
    import psutil
    from time import time

    # Disk usage
    disk_usage = shutil.disk_usage("/")
    disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
    disk_free_gb = disk_usage.free / (1024 ** 3)
    disk_total_gb = disk_usage.total / (1024 ** 3)

    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage_percent = memory.percent

    # Uptime (approximate based on downloads table)
    first_download = db.query(DownloadRecord).order_by(
        DownloadRecord.created_at.asc()
    ).first()

    uptime_seconds = 0
    if first_download and first_download.created_at:
        uptime_seconds = (datetime.utcnow() - first_download.created_at).total_seconds()

    return SystemHealth(
        disk_usage_percent=round(disk_usage_percent, 2),
        disk_free_gb=round(disk_free_gb, 2),
        disk_total_gb=round(disk_total_gb, 2),
        memory_usage_percent=round(memory_usage_percent, 2),
        uptime_seconds=round(uptime_seconds, 2),
    )


@router.get("/popular-categories")
async def get_popular_categories(
    limit: int = 10,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get most popular OS categories.
    """
    categories = db.query(
        DownloadRecord.os_category,
        func.count(DownloadRecord.id).label('count')
    ).filter(
        DownloadRecord.state == DownloadState.COMPLETED.value
    ).group_by(
        DownloadRecord.os_category
    ).order_by(desc('count')).limit(limit).all()

    return [
        {"category": cat, "count": count}
        for cat, count in categories
    ]
