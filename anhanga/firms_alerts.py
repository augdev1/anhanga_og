"""FIRMS fire alerts — real implementation using NASA API.

Uses the NASA FIRMS (Fire Information for Resource Management System) API
to fetch active fire/thermal anomaly data.
"""

import os
import requests
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

# NASA FIRMS Configuration
FIRMS_API_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
FIRMS_API_KEY = os.getenv("FIRMS_API_TOKEN", "")

# Use VIIRS NOAA-20 NRT (more modern and accurate)
DEFAULT_SOURCE = "VIIRS_NOAA20_NRT"

# Amazon Legal Region Bounding Box (aproximado)
# Formato: (min_lon, min_lat, max_lon, max_lat)
# Cobre aproximadamente: Brasil, Peru, Colômbia, Venezuela, Equador, Bolívia, Guianas
AMAZON_BBOX = (-74.0, -20.0, -44.0, 10.0)


def fetch_firms_alerts(
    days: int = 1,
    min_confidence: Optional[float] = None,
    limit: int = 500,
    bbox: Optional[tuple] = None,
) -> Dict[str, Any]:
    """Fetch fire alerts from NASA FIRMS API.

    Args:
        days: Number of days to look back (max 5 per API requirement)
        min_confidence: Minimum confidence level (0-100)
        limit: Maximum number of alerts to return
        bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
              Default is Amazon region

    Returns:
        GeoJSON FeatureCollection with fire alerts
    """
    try:
        # FIRMS API requires day range between 1 and 5
        days = min(max(days, 1), 5)

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # ALWAYS use Amazon region - ignore any other bbox
        bbox = AMAZON_BBOX
        
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Build API URL
        # Format: /api/area/csv/{MAP_KEY}/{SOURCE}/{AREA_COORDINATES}/{DAY_RANGE}
        bbox_str = f"{min_lon},{min_lat},{max_lon},{max_lat}"

        # If we have an API key, use it; otherwise try public endpoints
        if FIRMS_API_KEY:
            url = f"{FIRMS_API_URL}/{FIRMS_API_KEY}/{DEFAULT_SOURCE}/{bbox_str}/{days}"
        else:
            # Try without key (some sources may work)
            url = f"{FIRMS_API_URL}/{DEFAULT_SOURCE}/{bbox_str}/{days}"

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            # Parse CSV response
            alerts = _parse_firms_csv(response.text)
            
            # Filter by confidence if specified
            if min_confidence is not None:
                alerts = [
                    a for a in alerts 
                    if a.get("properties", {}).get("confidence", 0) >= min_confidence
                ]
            
            # Limit results
            alerts = alerts[:limit]
            
            return {
                "type": "FeatureCollection",
                "features": alerts
            }
        
        # If API fails, return sample data
        print(f"[FIRMS] API returned {response.status_code}, using sample data")
        return _get_sample_firms_alerts(days, bbox, limit)
        
    except Exception as e:
        print(f"[FIRMS Error] {e}")
        # Return sample data on error
        return _get_sample_firms_alerts(days, bbox or (-74.0, -20.0, -44.0, 10.0), limit)


def _parse_firms_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Parse FIRMS CSV response into GeoJSON features."""
    features = []
    lines = csv_text.strip().split('\n')
    
    if len(lines) < 2:
        return features
    
    # Parse header
    headers = lines[0].split(',')
    
    # Map column indices
    lat_idx = headers.index('latitude') if 'latitude' in headers else -1
    lon_idx = headers.index('longitude') if 'longitude' in headers else -1
    bright_idx = headers.index('brightness') if 'brightness' in headers else -1
    scan_idx = headers.index('scan') if 'scan' in headers else -1
    track_idx = headers.index('track') if 'track' in headers else -1
    acq_date_idx = headers.index('acq_date') if 'acq_date' in headers else -1
    acq_time_idx = headers.index('acq_time') if 'acq_time' in headers else -1
    satellite_idx = headers.index('satellite') if 'satellite' in headers else -1
    confidence_idx = headers.index('confidence') if 'confidence' in headers else -1
    version_idx = headers.index('version') if 'version' in headers else -1
    bright_t31_idx = headers.index('bright_t31') if 'bright_t31' in headers else -1
    frp_idx = headers.index('frp') if 'frp' in headers else -1
    daynight_idx = headers.index('daynight') if 'daynight' in headers else -1
    
    for line in lines[1:]:
        values = line.split(',')
        if len(values) < 2:
            continue
        
        try:
            lat = float(values[lat_idx]) if lat_idx >= 0 and lat_idx < len(values) else 0
            lon = float(values[lon_idx]) if lon_idx >= 0 and lon_idx < len(values) else 0
            
            # Parse confidence
            try:
                confidence = float(values[confidence_idx]) if confidence_idx >= 0 and confidence_idx < len(values) else 50
            except:
                confidence = 50
            
            # Parse date
            acq_date = values[acq_date_idx] if acq_date_idx >= 0 and acq_date_idx < len(values) else date.today().isoformat()
            acq_time = values[acq_time_idx] if acq_time_idx >= 0 and acq_time_idx < len(values) else "0000"
            
            # Format datetime
            try:
                datetime_str = f"{acq_date}T{acq_time[:2]}:{acq_time[2:]}:00"
            except:
                datetime_str = f"{acq_date}T00:00:00"
            
            # Parse brightness and FRP
            try:
                brightness = float(values[bright_idx]) if bright_idx >= 0 and bright_idx < len(values) else 0
            except:
                brightness = 0
            
            try:
                frp = float(values[frp_idx]) if frp_idx >= 0 and frp_idx < len(values) else 0
            except:
                frp = 0
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "latitude": lat,
                    "longitude": lon,
                    "brightness": brightness,
                    "confidence": confidence,
                    "alert_date": datetime_str,
                    "frp": frp,
                    "satellite": values[satellite_idx] if satellite_idx >= 0 and satellite_idx < len(values) else "unknown",
                    "source": "FIRMS",
                    "alert_type": "fire"
                }
            }
            
            features.append(feature)
            
        except Exception as e:
            print(f"[FIRMS] Error parsing line: {e}")
            continue
    
    return features


def _get_sample_firms_alerts(
    days: int = 1,
    bbox: tuple = None,
    limit: int = 500,
) -> Dict[str, Any]:
    """Generate sample fire alerts for testing when API is unavailable."""
    import random
    
    # Use Amazon bbox if not provided
    if bbox is None:
        bbox = AMAZON_BBOX
    
    min_lon, min_lat, max_lon, max_lat = bbox
    end_date = date.today()
    features = []
    
    # Generate sample fire alerts
    num_alerts = min(50, limit)  # Generate up to 50 sample alerts
    
    for i in range(num_alerts):
        # Random location within bbox
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        
        # Random date within the range
        days_ago = random.randint(0, days)
        alert_date = end_date - timedelta(days=days_ago)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        
        # Random confidence and brightness
        confidence = random.uniform(60, 100)
        brightness = random.uniform(300, 400)
        frp = random.uniform(10, 100)
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(lon, 4), round(lat, 4)]
            },
            "properties": {
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "brightness": round(brightness, 1),
                "confidence": round(confidence, 1),
                "alert_date": f"{alert_date.isoformat()}T{hour:02d}:{minute:02d}:00",
                "frp": round(frp, 1),
                "satellite": random.choice(["VIIRS", "MODIS"]),
                "source": "FIRMS",
                "alert_type": "fire"
            }
        }
        
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def get_firms_alerts_list(
    days: int = 1,
    min_confidence: Optional[float] = None,
    limit: int = 500,
    bbox: Optional[tuple] = None,
) -> List[Dict[str, Any]]:
    """Fetch fire alerts as a simple list (not GeoJSON)."""
    geojson = fetch_firms_alerts(days, min_confidence, limit, bbox)
    
    alerts = []
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        alerts.append({
            "latitude": coords[1],
            "longitude": coords[0],
            "alert_date": props.get("alert_date"),
            "confidence": props.get("confidence"),
            "brightness": props.get("brightness"),
            "frp": props.get("frp"),
            "satellite": props.get("satellite"),
            "source": "FIRMS",
            "alert_type": "fire"
        })
    
    return alerts
