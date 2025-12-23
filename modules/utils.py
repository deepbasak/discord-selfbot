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
    """Load configuration from config.json
    
    Supports multiple methods:
    1. Environment variable DISCORD_TOKEN (for deployments)
    2. config/config.json file (relative to script directory)
    3. config/config.json file (relative to current working directory)
    """
    # First, try environment variable (common in cloud deployments)
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        token = token.strip()  # Strip whitespace
        # Build config from environment variables
        config = {
            "token": token,
            "prefix": os.environ.get("DISCORD_PREFIX", "*"),
            "remote-users": os.environ.get("DISCORD_REMOTE_USERS", "").split(",") if os.environ.get("DISCORD_REMOTE_USERS") else [],
            "autoreply": {
                "messages": os.environ.get("DISCORD_AUTOREPLY_MESSAGES", "").split("|") if os.environ.get("DISCORD_AUTOREPLY_MESSAGES") else [],
                "channels": os.environ.get("DISCORD_AUTOREPLY_CHANNELS", "").split(",") if os.environ.get("DISCORD_AUTOREPLY_CHANNELS") else [],
                "users": os.environ.get("DISCORD_AUTOREPLY_USERS", "").split(",") if os.environ.get("DISCORD_AUTOREPLY_USERS") else []
            },
            "afk": {
                "enabled": os.environ.get("DISCORD_AFK_ENABLED", "false").lower() == "true",
                "message": os.environ.get("DISCORD_AFK_MESSAGE", "I am currently AFK!")
            },
            "copycat": {
                "users": os.environ.get("DISCORD_COPYCAT_USERS", "").split(",") if os.environ.get("DISCORD_COPYCAT_USERS") else []
            },
            "selenium": {
                "headless": os.environ.get("DISCORD_SELENIUM_HEADLESS", "true").lower() == "true",
                "implicit_wait": int(os.environ.get("DISCORD_SELENIUM_IMPLICIT_WAIT", "10")),
                "page_load_timeout": int(os.environ.get("DISCORD_SELENIUM_PAGE_LOAD_TIMEOUT", "30")),
                "window_size": {
                    "width": int(os.environ.get("DISCORD_SELENIUM_WIDTH", "1920")),
                    "height": int(os.environ.get("DISCORD_SELENIUM_HEIGHT", "1080"))
                }
            },
            "tts": {
                "provider": os.environ.get("DISCORD_TTS_PROVIDER", "elevenlabs"),
                "default_voice": os.environ.get("DISCORD_TTS_VOICE", "default"),
                "save_path": os.environ.get("DISCORD_TTS_SAVE_PATH", "temp/tts")
            }
        }
        print(f"[INFO] Loaded configuration from environment variables")
        return config
    
    # Try to find config file using absolute path based on script location
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_paths = [
        os.path.join(script_dir, "config", "config.json"),  # Relative to main.py location
        os.path.join("config", "config.json"),  # Relative to current working directory
        os.path.abspath(os.path.join("config", "config.json")),  # Absolute from CWD
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Strip token whitespace if present
                    if "token" in config and isinstance(config["token"], str):
                        config["token"] = config["token"].strip()
                    print(f"[INFO] Loaded configuration from: {config_path}")
                    return config
            except json.JSONDecodeError as e:
                print(f"[WARNING] Invalid JSON in config file {config_path}: {e}")
                continue
            except Exception as e:
                print(f"[WARNING] Error reading config file {config_path}: {e}")
                continue
    
    # If no config found, try to create from example
    example_path = os.path.join(script_dir, "config", "config.json.example")
    if os.path.exists(example_path):
        print(f"[WARNING] config.json not found. Attempting to create from example...")
        try:
            with open(example_path, "r", encoding="utf-8") as f:
                example_config = json.load(f)
            # Create config directory if it doesn't exist
            config_dir = os.path.join(script_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(example_config, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Created config.json from example at: {config_path}")
            return example_config
        except Exception as e:
            print(f"[ERROR] Failed to create config from example: {e}")
    
    # Last resort: return empty dict
    print(f"[WARNING] No configuration found. Tried paths: {config_paths}")
    print(f"[INFO] Current working directory: {os.getcwd()}")
    print(f"[INFO] Script directory: {script_dir}")
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
