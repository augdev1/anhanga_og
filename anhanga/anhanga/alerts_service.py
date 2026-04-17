"""Unified alerts service — stub implementation.

Replace with real API calls to GFW / FIRMS / Landsat when credentials are available.
"""

from datetime import date
from typing import Any, Dict, List, Optional


def get_map_alerts(
    days: int = 14,
    confidence: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return []


def get_map_alerts_with_stats(
    days: int = 14,
    confidence: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 1000,
) -> Dict[str, Any]:
    return {
        "alerts": [],
        "source_counts_raw": {},
        "source_counts_final": {},
        "confidence_counts": {},
        "source_errors": {},
    }


def get_map_clusters(
    days: int = 14,
    confidence: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    eps_km: float = 1.0,
    min_samples: int = 1,
) -> List[Dict[str, Any]]:
    return []


def alerts_to_geojson(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "FeatureCollection", "features": []}
