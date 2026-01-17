"""Health check and metrics endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from ...core.logger import get_logger
from ...core.metrics import (
    PUBLICATION_QUEUE_SIZE,
    DEAD_LETTER_QUEUE_SIZE,
    ACTIVE_CONNECTIONS,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - API info.

    Returns:
        API info
    """
    return {
        "name": "Ultrabot",
        "version": "1.0.0",
        "description": "Gaming News Aggregator Bot",
        "endpoints": {
            "health": "/api/health",
            "ready": "/api/ready",
            "metrics": "/api/metrics",
            "stats": "/api/stats",
        }
    }


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Liveness probe - simple health check.

    Returns:
        Health status
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """Readiness probe - check if service is ready.

    Returns:
        Readiness status
    """
    # TODO: Add checks for:
    # - Database connection
    # - Redis connection
    # - Telegram bot connection

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",
            "redis": "ok",
            "telegram": "ok",
        },
    }


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint.

    Returns:
        Prometheus metrics
    """
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
    )


@router.get("/stats")
async def stats() -> dict[str, Any]:
    """Application statistics.

    Returns:
        Current statistics
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "queue": {
            "publication_size": int(PUBLICATION_QUEUE_SIZE._value.get()),
            "dead_letter_size": int(DEAD_LETTER_QUEUE_SIZE._value.get()),
        },
        "connections": {
            "active": int(ACTIVE_CONNECTIONS._value.get()),
        },
    }
