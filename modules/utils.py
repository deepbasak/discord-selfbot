"""
Utility functions for the Discord selfbot
"""

import os
import time
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import qrcode
from PIL import Image
import io
import base64


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = os.path.join("config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Any]):
    """Save configuration to config.json"""
    config_path = os.path.join("config", "config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_uptime(start_time: float) -> str:
    """Calculate uptime from start time"""
    uptime_seconds = time.time() - start_time
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def ping_website(url: str) -> Dict[str, Any]:
    """Ping a website and return status information"""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "status_code": response.status_code,
            "response_time": f"{elapsed_time:.2f}ms",
            "online": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": None,
            "response_time": None,
            "online": False,
            "error": str(e)
        }


def geoip_lookup(ip: str) -> Dict[str, Any]:
    """Look up IP geolocation information"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "timezone": data.get("timezone")
            }
        else:
            return {"error": "Failed to lookup IP"}
    except Exception as e:
        return {"error": str(e)}


def generate_qr_code(text: str) -> io.BytesIO:
    """Generate QR code image from text"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


def reverse_text(text: str) -> str:
    """Reverse text"""
    return text[::-1]


def generate_fake_token() -> str:
    """Generate a fake but correctly formatted Discord token"""
    import random
    import string
    
    # Discord tokens have format: base64_user_id.base64_timestamp.base64_hmac
    user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=18))
    timestamp = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hmac = ''.join(random.choices(string.ascii_letters + string.digits, k=27))
    
    return f"{user_id}.{timestamp}.{hmac}"


def create_temp_dir() -> str:
    """Create temporary directory if it doesn't exist"""
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def clean_temp_files(older_than_hours: int = 24):
    """Clean temporary files older than specified hours"""
    temp_dir = create_temp_dir()
    current_time = time.time()
    cutoff_time = current_time - (older_than_hours * 3600)
    
    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                except:
                    pass
