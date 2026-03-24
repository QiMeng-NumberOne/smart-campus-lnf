import math
from datetime import datetime

def calc_location_score(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate location similarity score [0, 1] based on Haversine distance.
    Decay constant determines how fast the score drops over distance.
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    # Haversine formula
    R = 6371000  # Radius of earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi_1) * math.cos(phi_2) *
         math.sin(delta_lambda / 2.0) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_meters = R * c

    # Convert distance to score (exponential decay)
    # E.g., drops to ~0.36 at 1000 meters
    decay_constant = 1000.0  
    score = math.exp(-distance_meters / decay_constant)
    return max(0.0, min(1.0, float(score)))

def calc_time_score(time1_iso: str, time2_iso: str) -> float:
    """
    Calculate time similarity score [0, 1] based on hour difference.
    Expected ISO format strings like "2026-03-23T10:00:00"
    """
    if not time1_iso or not time2_iso:
        return 0.0
    
    try:
        t1 = datetime.fromisoformat(time1_iso.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(time2_iso.replace("Z", "+00:00"))
        diff_hours = abs((t1 - t2).total_seconds()) / 3600.0
        
        # Exponential decay: score is ~0.36 at 48 hours difference
        decay_hours = 48.0
        score = math.exp(-diff_hours / decay_hours)
        return max(0.0, min(1.0, float(score)))
    except Exception:
        return 0.0
