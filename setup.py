"""
Setup script for the Discord SelfBot
"""

import os
import sys
import subprocess


def install_requirements():
    """Install required packages"""
    print("📦 Upgrading pip, setuptools, and wheel...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not upgrade pip/setuptools/wheel")
    
    print("📦 Installing requirements...")
    try:
        # Prefer binary wheels to avoid building from source
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--prefer-binary", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing requirements")
        print("💡 Tip: If packages fail to build, you may need to install Microsoft Visual C++ Build Tools")
        print("   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    directories = ["config", "temp", "modules"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created")


def check_config():
    """Check if config file exists"""
    if not os.path.exists("config/config.json"):
        print("⚠️  Config file not found. Please create config/config.json")
        print("   See config/config.json.example for reference")
    else:
        print("✅ Config file exists")


if __name__ == "__main__":
    print("=" * 50)
    print("Discord SelfBot Setup")
    print("=" * 50)
    
    create_directories()
    install_requirements()
    check_config()
    
    print("=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit config/config.json and add your Discord token")
    print("2. Run: python main.py")
