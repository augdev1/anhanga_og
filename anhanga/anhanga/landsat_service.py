"""Landsat satellite alerts — stub implementation.

Replace with real Landsat API calls when credentials are available.
"""

from datetime import date
from typing import Any, Dict, List, Optional


def get_landsat_alerts_amazon(
    days: int = 14,
    confidence: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Optional[List[Dict[str, Any]]]:
    return []
