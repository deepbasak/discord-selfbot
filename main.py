"""
Discord SelfBot - All-in-One
Supports Replit and local deployment
"""

# ==================== CONFIGURATION ====================
# ⚠️ IMPORTANT: Replace YOUR_TOKEN_HERE with your actual Discord token
# ⚠️ DO NOT commit your real token to GitHub - it will be blocked!
# Paste your Discord token here:
TOKEN = "YOUR_TOKEN_HERE"

# Optional settings:
PREFIX = "*"  # Command prefix
# =======================================================

import os
import sys
import subprocess

# ==================== AUTO INSTALL DEPENDENCIES ====================
def install_requirements():
    """Auto-install missing packages"""
    required_packages = {
        "discord.py-self": "discord.py-self==2.0.0",
        "audioop_lts": "audioop-lts>=0.2.2",
        "selenium": "selenium==4.15.2",
        "webdriver_manager": "webdriver-manager==4.0.1",
        "requests": "requests==2.31.0",
        "PIL": "Pillow>=10.4.0",
        "qrcode": "qrcode==7.4.2",
        "aiohttp": "aiohttp>=3.11.0",
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            if module == "PIL":
                __import__("PIL")
            elif module == "audioop_lts":
                __import__("audioop")
            else:
                __import__(module.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print("📦 Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "pip", "setuptools", "wheel"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--prefer-binary"] + missing)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Some packages failed to install. You may need to install them manually:")
            print(f"   pip install {' '.join(missing)}")
            print("   Continuing anyway...")

# Install dependencies before importing
install_requirements()

import asyncio
import time
import json
import random
import string
import re
import io
import requests
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime

# Discord
import discord

# QR Code
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except:
    QR_AVAILABLE = False

# Selenium (optional - only if available)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False

# ==================== DISCORD PATCH ====================
def patch_discord_state():
    try:
        from discord import state as discord_state
        original_parse_ready_supplemental = discord_state.ConnectionState.parse_ready_supplemental
        
        async def patched_parse_ready_supplemental(self, data):
            pending_payments_raw = data.get('pending_payments')
            pending_payments_data = pending_payments_raw if pending_payments_raw is not None else []
            try:
                Payment = getattr(discord_state, 'Payment', None)
                if Payment:
                    self.pending_payments = {int(p['id']): Payment(state=self, data=p) for p in pending_payments_data}
                else:
                    self.pending_payments = {int(p['id']): p for p in pending_payments_data if p and 'id' in p}
            except:
                self.pending_payments = {}
            
            connected_accounts_raw = data.get('connected_accounts')
            connected_accounts_data = connected_accounts_raw if connected_accounts_raw is not None else []
            try:
                ConnectedAccount = getattr(discord_state, 'ConnectedAccount', None)
                if ConnectedAccount:
                    self.connected_accounts = {int(acc['id']): ConnectedAccount(state=self, data=acc) for acc in connected_accounts_data}
                else:
                    self.connected_accounts = {int(acc['id']): acc for acc in connected_accounts_data if acc and 'id' in acc}
            except:
                self.connected_accounts = {}
        
        discord_state.ConnectionState.parse_ready_supplemental = patched_parse_ready_supplemental
    except:
        pass

# ==================== CONFIG ====================
def load_config():
    """Load config from main.py variables, environment, or defaults"""
    # Priority: 1. TOKEN variable in main.py, 2. Environment variable, 3. Default
    token = TOKEN if TOKEN != "YOUR_TOKEN_HERE" else (os.environ.get("TOKEN") or os.environ.get("DISCORD_TOKEN") or "")
    
    return {
        "token": token.strip() if token else "",
        "prefix": PREFIX if PREFIX else (os.environ.get("PREFIX", "*")),
        "remote-users": os.environ.get("REMOTE_USERS", "").split(",") if os.environ.get("REMOTE_USERS") else [],
        "selenium": {"headless": os.environ.get("SELENIUM_HEADLESS", "true").lower() == "true"}
    }

def save_config(config):
    """Save config - updates TOKEN and PREFIX in main.py"""
    # Note: This doesn't actually modify the file, just updates in-memory config
    # The token is stored directly in the TOKEN variable at the top of main.py
    pass

# ==================== UTILITIES ====================
def get_uptime(start_time):
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

def ping_website(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        elapsed_time = (time.time() - start_time) * 1000
        return {"status_code": response.status_code, "response_time": f"{elapsed_time:.2f}ms", "online": response.status_code == 200}
    except Exception as e:
        return {"status_code": None, "response_time": None, "online": False, "error": str(e)}

def geoip_lookup(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return {"country": data.get("country"), "region": data.get("regionName"), "city": data.get("city"), "isp": data.get("isp"), "timezone": data.get("timezone")}
        else:
            return {"error": "Failed to lookup IP"}
    except Exception as e:
        return {"error": str(e)}

def generate_qr_code(text):
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def reverse_text(text):
    return text[::-1]

def generate_fake_token():
    user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=18))
    timestamp = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hmac = ''.join(random.choices(string.ascii_letters + string.digits, k=27))
    return f"{user_id}.{timestamp}.{hmac}"

# ==================== SELENIUM SCRAPER ====================
class SeleniumScraper:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.headless = config.get("selenium", {}).get("headless", True)
    
    async def initialize_driver(self):
        if not SELENIUM_AVAILABLE:
            return False
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_argument("--log-level=3")
            try:
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            return True
        except:
            return False
    
    async def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    async def take_screenshot(self, url, save_path):
        if not self.driver:
            if not await self.initialize_driver():
                return None
        try:
            self.driver.get(url)
            await asyncio.sleep(3)
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
            self.driver.save_screenshot(save_path)
            return save_path
        except:
            return None
    
    async def scrape_website_content(self, url, selectors):
        if not self.driver:
            if not await self.initialize_driver():
                return {}
        try:
            self.driver.get(url)
            await asyncio.sleep(3)
            results = {}
            for key, selector in selectors.items():
                try:
                    element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    results[key] = element.text if element.text else element.get_attribute("innerHTML")
                except:
                    results[key] = None
            return results
        except:
            return {}
    
    async def download_file(self, url, save_path):
        if not self.driver:
            if not await self.initialize_driver():
                return None
        try:
            self.driver.get(url)
            await asyncio.sleep(2)
            return save_path if os.path.exists(save_path) else None
        except:
            return None

# ==================== COMMAND HANDLER ====================
class CommandHandler:
    def __init__(self, bot, config, start_time, bot_instance=None):
        self.bot = bot
        self.config = config
        self.start_time = start_time
        self.bot_instance = bot_instance
        self.scraper = SeleniumScraper(config) if SELENIUM_AVAILABLE else None
        self.afk_users = {}
        self.copycat_users = set()
        
        self.command_map = {
            "help": self.cmd_help, "h": self.cmd_help,
            "shutdown": self.cmd_shutdown,
            "uptime": self.cmd_uptime,
            "ping": self.cmd_ping,
            "changeprefix": self.cmd_changeprefix,
            "remoteuser": self.cmd_remoteuser,
            "copycat": self.cmd_copycat,
            "pingweb": self.cmd_pingweb,
            "geoip": self.cmd_geoip,
            "qr": self.cmd_qr,
            "reverse": self.cmd_reverse,
            "edit": self.cmd_edit,
            "hidemention": self.cmd_hidemention,
            "screenshot": self.cmd_screenshot,
            "scrape": self.cmd_scrape,
            "download": self.cmd_download,
            "purge": self.cmd_purge,
            "clear": self.cmd_clear,
            "cleardm": self.cmd_cleardm,
            "spam": self.cmd_spam,
            "quickdelete": self.cmd_quickdelete,
            "autoreply": self.cmd_autoreply,
            "afk": self.cmd_afk,
            "guildinfo": self.cmd_guildinfo,
            "guildicon": self.cmd_guildicon,
            "guildbanner": self.cmd_guildbanner,
            "guildrename": self.cmd_guildrename,
            "fetchmembers": self.cmd_fetchmembers,
            "usericon": self.cmd_usericon,
            "dmall": self.cmd_dmall,
            "sendall": self.cmd_sendall,
            "playing": self.cmd_playing,
            "watching": self.cmd_watching,
            "stopactivity": self.cmd_stopactivity,
            "gentoken": self.cmd_gentoken,
            "hypesquad": self.cmd_hypesquad,
            "nitro": self.cmd_nitro,
            "ascii": self.cmd_ascii,
            "minesweeper": self.cmd_minesweeper,
            "leetpeek": self.cmd_leetpeek,
            "whremove": self.cmd_whremove,
            "firstmessage": self.cmd_firstmessage,
        }
    
    async def safe_edit(self, message, content):
        if message.author.id == self.bot.user.id:
            try:
                await message.edit(content=content)
            except:
                try:
                    await message.channel.send(content)
                except:
                    pass
        else:
            try:
                await message.channel.send(content)
            except:
                pass
    
    async def handle_command(self, message, command, args):
        command = command.lower()
        handler = self.command_map.get(command)
        if handler:
            if command in ("shutdown", "uptime", "ping", "guildinfo", "guildicon", "guildbanner", "fetchmembers", "stopactivity", "gentoken", "nitro", "firstmessage"):
                await handler(message)
            else:
                await handler(message, args)
            return True
        return False
    
    async def cmd_help(self, message, args):
        prefix = self.config.get("prefix", "*")
        help_text = f"""```yaml
╔══════════════════════════════════════════════════════════╗
║           Discord SelfBot - Commands                     ║
╚══════════════════════════════════════════════════════════╝

[Basic]
{prefix}help - Show this menu
{prefix}ping - Check latency
{prefix}uptime - Show uptime
{prefix}changeprefix <prefix> - Change prefix
{prefix}shutdown - Stop bot

[Web]
{prefix}pingweb <url> - Ping website
{prefix}geoip <ip> - IP lookup
{prefix}qr <text> - Generate QR code
{prefix}screenshot <url> - Screenshot website
{prefix}scrape <url> - Scrape website

[Message]
{prefix}reverse <text> - Reverse text
{prefix}edit <text> - Edit message
{prefix}purge <amount> - Delete messages
{prefix}clear <amount> - Clear messages

[Server]
{prefix}guildinfo - Server info
{prefix}guildicon - Server icon
{prefix}usericon <@user> - User avatar
{prefix}dmall <message> - DM all members
{prefix}sendall <message> - Send to all channels

[Activity]
{prefix}playing <status> - Set playing
{prefix}watching <status> - Set watching
{prefix}stopactivity - Clear activity

[Fun]
{prefix}gentoken - Fake token
{prefix}hypesquad <house> - Change badge
{prefix}nitro - Fake nitro
{prefix}ascii <text> - ASCII art
{prefix}minesweeper - Play game
```"""
        await self.safe_edit(message, help_text)
    
    async def cmd_shutdown(self, message):
        await self.safe_edit(message, "🛑 Shutting down...")
        if self.scraper:
            await self.scraper.cleanup()
        await self.bot.close()
    
    async def cmd_uptime(self, message):
        uptime = get_uptime(self.start_time)
        await self.safe_edit(message, f"⏱️ Uptime: {uptime}")
    
    async def cmd_ping(self, message):
        latency = round(self.bot.latency * 1000, 2)
        await self.safe_edit(message, f"🏓 Pong! {latency}ms")
    
    async def cmd_changeprefix(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide prefix")
            return
        new_prefix = args[0]
        self.config["prefix"] = new_prefix
        save_config(self.config)
        if self.bot_instance:
            self.bot_instance.prefix = new_prefix
        await self.safe_edit(message, f"✅ Prefix: `{new_prefix}`")
    
    async def cmd_remoteuser(self, message, args):
        if len(args) < 2:
            await self.safe_edit(message, "❌ Usage: `remoteuser ADD|REMOVE <@user>`")
            return
        action = args[0].upper()
        remote_users = self.config.get("remote-users", [])
        for user in message.mentions:
            user_id = str(user.id)
            if action == "ADD" and user_id not in remote_users:
                remote_users.append(user_id)
                await self.safe_edit(message, f"✅ Added {user.mention}")
            elif action == "REMOVE" and user_id in remote_users:
                remote_users.remove(user_id)
                await self.safe_edit(message, f"✅ Removed {user.mention}")
        self.config["remote-users"] = remote_users
        save_config(self.config)
    
    async def cmd_copycat(self, message, args):
        if len(args) < 2 or not message.mentions:
            await self.safe_edit(message, "❌ Usage: `copycat ON|OFF <@user>`")
            return
        mode = args[0].upper()
        user_id = message.mentions[0].id
        if mode == "ON":
            self.copycat_users.add(user_id)
            await self.safe_edit(message, f"✅ Copycat ON for {message.mentions[0].mention}")
        elif mode == "OFF":
            self.copycat_users.discard(user_id)
            await self.safe_edit(message, f"✅ Copycat OFF")
    
    async def cmd_pingweb(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide URL")
            return
        result = ping_website(args[0])
        if result.get("online"):
            await self.safe_edit(message, f"🌐 {args[0]}\n✅ {result['status_code']} | {result['response_time']}")
        else:
            await self.safe_edit(message, f"❌ Offline")
    
    async def cmd_geoip(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide IP")
            return
        result = geoip_lookup(args[0])
        if "error" in result:
            await self.safe_edit(message, f"❌ {result['error']}")
        else:
            info = f"🌍 {args[0]}\n📍 {result.get('country', 'N/A')}\n🏙️ {result.get('city', 'N/A')}\n🌐 {result.get('isp', 'N/A')}"
            await self.safe_edit(message, info)
    
    async def cmd_qr(self, message, args):
        if not args or not QR_AVAILABLE:
            await self.safe_edit(message, "❌ Provide text" if args else "❌ QR code not available")
            return
        qr_img = generate_qr_code(" ".join(args))
        if qr_img:
            await self.safe_edit(message, "📱 QR Code:")
            await message.channel.send(file=discord.File(qr_img, filename="qrcode.png"))
    
    async def cmd_reverse(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide text")
            return
        await self.safe_edit(message, reverse_text(" ".join(args)))
    
    async def cmd_edit(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide text")
            return
        await self.safe_edit(message, f"{' '.join(args)} (edited)")
    
    async def cmd_hidemention(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide text")
            return
        hidden = " ".join(args).replace("@", "@\u200b")
        await self.safe_edit(message, hidden)
    
    async def cmd_screenshot(self, message, args):
        if not args or not self.scraper:
            await self.safe_edit(message, "❌ Provide URL" if args else "❌ Selenium not available")
            return
        url = args[0]
        await self.safe_edit(message, "📸 Taking screenshot...")
        os.makedirs("temp", exist_ok=True)
        filepath = f"temp/screenshot_{int(time.time())}.png"
        screenshot_path = await self.scraper.take_screenshot(url, filepath)
        if screenshot_path and os.path.exists(screenshot_path):
            await self.safe_edit(message, f"📸 Screenshot:")
            await message.channel.send(file=discord.File(screenshot_path))
            await asyncio.sleep(5)
            try:
                os.remove(screenshot_path)
            except:
                pass
        else:
            await self.safe_edit(message, "❌ Failed")
    
    async def cmd_scrape(self, message, args):
        if not args or not self.scraper:
            await self.safe_edit(message, "❌ Provide URL" if args else "❌ Selenium not available")
            return
        await self.safe_edit(message, "🔍 Scraping...")
        result = await self.scraper.scrape_website_content(args[0], {"title": "title", "content": "body"})
        if result:
            content = f"📄 {args[0]}:\n"
            for key, value in result.items():
                if value:
                    content += f"**{key}**: {value[:300]}...\n"
            await self.safe_edit(message, content[:2000])
        else:
            await self.safe_edit(message, "❌ Failed")
    
    async def cmd_download(self, message, args):
        if not args or not self.scraper:
            await self.safe_edit(message, "❌ Provide URL" if args else "❌ Selenium not available")
            return
        await self.safe_edit(message, "⬇️ Downloading...")
        os.makedirs("temp", exist_ok=True)
        filepath = f"temp/download_{int(time.time())}"
        downloaded = await self.scraper.download_file(args[0], filepath)
        if downloaded and os.path.exists(downloaded):
            await self.safe_edit(message, "⬇️ Downloaded:")
            await message.channel.send(file=discord.File(downloaded))
        else:
            await self.safe_edit(message, "❌ Failed")
    
    async def cmd_purge(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide amount")
            return
        try:
            amount = int(args[0])
            if amount <= 0:
                await self.safe_edit(message, "❌ Amount > 0")
                return
            try:
                await message.delete()
            except:
                pass
            deleted = await message.channel.purge(limit=amount)
            confirmation = await message.channel.send(f"✅ Deleted {len(deleted) + 1} messages")
            await asyncio.sleep(3)
            try:
                await confirmation.delete()
            except:
                pass
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_clear(self, message, args):
        amount = int(args[0]) if args and args[0].isdigit() else 100
        await self.cmd_purge(message, [str(amount)])
    
    async def cmd_cleardm(self, message, args):
        if not args or not isinstance(message.channel, discord.DMChannel):
            await self.safe_edit(message, "❌ Provide amount")
            return
        try:
            amount = int(args[0]) + 1
            deleted = await message.channel.purge(limit=amount)
            await message.channel.send(f"✅ Deleted {len(deleted)} messages")
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_spam(self, message, args):
        if len(args) < 2:
            await self.safe_edit(message, "❌ Usage: `spam <amount> <message>`")
            return
        try:
            amount = min(int(args[0]), 20)
            spam_text = " ".join(args[1:])
            for _ in range(amount):
                await message.channel.send(spam_text)
                await asyncio.sleep(0.5)
            await message.delete()
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_quickdelete(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide message")
            return
        sent = await message.channel.send(" ".join(args))
        await message.delete()
        await asyncio.sleep(2)
        await sent.delete()
    
    async def cmd_autoreply(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Usage: `autoreply ON|OFF`")
            return
        await self.safe_edit(message, f"✅ Auto-reply: {args[0].upper()}")
    
    async def cmd_afk(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Usage: `afk ON|OFF [message]`")
            return
        mode = args[0].upper()
        afk_message = " ".join(args[1:]) if len(args) > 1 else "I am AFK"
        bot_user_id = self.bot.user.id
        if mode == "ON":
            self.afk_users[bot_user_id] = afk_message
            await self.safe_edit(message, f"✅ AFK: {afk_message}")
        elif mode == "OFF":
            self.afk_users.pop(bot_user_id, None)
            await self.safe_edit(message, "✅ AFK disabled")
    
    async def cmd_guildinfo(self, message):
        if not message.guild:
            await self.safe_edit(message, "❌ Server only")
            return
        guild = message.guild
        info = f"""📊 {guild.name}
🆔 {guild.id}
👑 {guild.owner.mention if guild.owner else 'N/A'}
👥 {guild.member_count}
📅 {guild.created_at.strftime('%Y-%m-%d')}
📁 {len(guild.channels)} channels"""
        await self.safe_edit(message, info)
    
    async def cmd_guildicon(self, message):
        if not message.guild or not message.guild.icon:
            await self.safe_edit(message, "❌ No icon")
            return
        await self.safe_edit(message, f"🖼️ {message.guild.icon.url}")
    
    async def cmd_guildbanner(self, message):
        if not message.guild or not message.guild.banner:
            await self.safe_edit(message, "❌ No banner")
            return
        await self.safe_edit(message, f"🎨 {message.guild.banner.url}")
    
    async def cmd_guildrename(self, message, args):
        if not message.guild or not args:
            await self.safe_edit(message, "❌ Provide name")
            return
        try:
            await message.guild.edit(name=" ".join(args))
            await self.safe_edit(message, f"✅ Renamed to: {' '.join(args)}")
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_fetchmembers(self, message):
        if not message.guild:
            await self.safe_edit(message, "❌ Server only")
            return
        members = [str(m) for m in message.guild.members]
        member_list = "\n".join(members[:50])
        await self.safe_edit(message, f"👥 {len(members)} members:\n{member_list}")
    
    async def cmd_usericon(self, message, args):
        user = message.mentions[0] if message.mentions else message.author
        await self.safe_edit(message, f"🖼️ {user.name}: {user.avatar.url if user.avatar else 'No avatar'}")
    
    async def cmd_dmall(self, message, args):
        if not message.guild or not args:
            await self.safe_edit(message, "❌ Server only + message")
            return
        text = " ".join(args)
        count = 0
        for member in message.guild.members:
            if member.id != self.bot.user.id:
                try:
                    await member.send(text)
                    count += 1
                    await asyncio.sleep(1)
                except:
                    pass
        await self.safe_edit(message, f"✅ Sent to {count} members")
    
    async def cmd_sendall(self, message, args):
        if not message.guild or not args:
            await self.safe_edit(message, "❌ Server only + message")
            return
        text = " ".join(args)
        count = 0
        for channel in message.guild.text_channels:
            try:
                await channel.send(text)
                count += 1
                await asyncio.sleep(0.5)
            except:
                pass
        await self.safe_edit(message, f"✅ Sent to {count} channels")
    
    async def cmd_playing(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide status")
            return
        activity = discord.Game(name=" ".join(args))
        await self.bot.change_presence(activity=activity)
        await self.safe_edit(message, f"✅ Playing: {' '.join(args)}")
    
    async def cmd_watching(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide status")
            return
        activity = discord.Activity(type=discord.ActivityType.watching, name=" ".join(args))
        await self.bot.change_presence(activity=activity)
        await self.safe_edit(message, f"✅ Watching: {' '.join(args)}")
    
    async def cmd_stopactivity(self, message):
        await self.bot.change_presence(activity=None)
        await self.safe_edit(message, "✅ Activity cleared")
    
    async def cmd_gentoken(self, message):
        await self.safe_edit(message, f"🎫 `{generate_fake_token()}`")
    
    async def cmd_hypesquad(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Usage: `hypesquad <bravery|brilliance|balance>`")
            return
        houses = {"bravery": 1, "brilliance": 2, "balance": 3}
        house = args[0].lower()
        if house not in houses:
            await self.safe_edit(message, "❌ Invalid house")
            return
        try:
            token = self.bot.http.token if hasattr(self.bot.http, 'token') else self.config.get("token")
            headers = {"Authorization": token, "Content-Type": "application/json"}
            url = "https://discord.com/api/v9/hypesquad/online"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"house_id": houses[house]}, headers=headers) as response:
                    if response.status == 204:
                        await self.safe_edit(message, f"✅ HypeSquad: {house.capitalize()}")
                    else:
                        await self.safe_edit(message, f"❌ Failed: {response.status}")
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_nitro(self, message):
        code = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(16)])
        await self.safe_edit(message, f"🎁 https://discord.gift/{code}")
    
    async def cmd_ascii(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide text")
            return
        ascii_text = "\n".join([char.upper() for char in " ".join(args)])
        await self.safe_edit(message, f"```\n{ascii_text}\n```")
    
    async def cmd_minesweeper(self, message, args):
        try:
            width = min(max(int(args[0]) if args else 9, 2), 15)
            height = min(max(int(args[1]) if len(args) > 1 else 9, 2), 15)
            grid = [[":zero:" for _ in range(width)] for _ in range(height)]
            grid_text = "\n".join(["".join(row) for row in grid])
            await self.safe_edit(message, grid_text[:2000])
        except:
            await self.safe_edit(message, "❌ Error")
    
    async def cmd_leetpeek(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide text")
            return
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'l': '1', 'g': '9'}
        leet_text = "".join([leet_map.get(char.lower(), char) for char in " ".join(args)])
        await self.safe_edit(message, leet_text)
    
    async def cmd_whremove(self, message, args):
        if not args:
            await self.safe_edit(message, "❌ Provide webhook URL")
            return
        try:
            webhook = discord.Webhook.from_url(args[0], session=self.bot.http._HTTPClient__session)
            await webhook.delete()
            await self.safe_edit(message, "✅ Deleted")
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")
    
    async def cmd_firstmessage(self, message):
        try:
            async for msg in message.channel.history(limit=1, oldest_first=True):
                await self.safe_edit(message, f"📌 {msg.jump_url}")
                break
        except Exception as e:
            await self.safe_edit(message, f"❌ {str(e)}")

# ==================== BOT ====================
class Bot:
    def __init__(self):
        patch_discord_state()
        self.config = load_config()
        self.token = self.config.get("token", "").strip() if self.config.get("token") else ""
        self.prefix = self.config.get("prefix", "*")
        self.start_time = time.time()
        
        if not self.token or self.token == "YOUR_TOKEN_HERE" or len(self.token) < 10:
            print("❌ Please set your token in main.py")
            print("   Edit the TOKEN variable at the top of main.py")
            print("   Example: TOKEN = 'your_discord_token_here'")
            sys.exit(1)
        
        self.bot = discord.Client()
        self.command_handler = CommandHandler(self.bot, self.config, self.start_time, self)
        self.setup_events()
    
    def setup_events(self):
        @self.bot.event
        async def on_ready():
            print(f"✅ Logged in as {self.bot.user.name}#{self.bot.user.discriminator}")
            print(f"🆔 {self.bot.user.id}")
            try:
                guilds = self.bot.guilds if hasattr(self.bot, 'guilds') and self.bot.guilds else []
                print(f"📊 {len(guilds)} servers")
            except:
                pass
            print("=" * 50)
        
        @self.bot.event
        async def on_message(message):
            if not message.content.startswith(self.prefix):
                if message.author.id == self.bot.user.id:
                    return
                if message.author.id in self.command_handler.copycat_users:
                    try:
                        await message.channel.send(message.content)
                    except:
                        pass
                if self.bot.user.mentioned_in(message) and self.bot.user.id in self.command_handler.afk_users:
                    try:
                        await message.reply(self.command_handler.afk_users[self.bot.user.id])
                    except:
                        pass
                return
            
            if message.author.id != self.bot.user.id:
                remote_users = self.config.get("remote-users", [])
                if remote_users and str(message.author.id) not in remote_users:
                    return
            
            parts = message.content[len(self.prefix):].strip().split()
            if not parts:
                return
            
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            try:
                result = await self.command_handler.handle_command(message, command, args)
                if result is False:
                    await self.command_handler.safe_edit(message, f"❌ Unknown: `{command}`\nType `{self.prefix}help`")
            except Exception as e:
                try:
                    await self.command_handler.safe_edit(message, f"❌ Error: {str(e)}")
                except:
                    pass
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            import traceback
            traceback.print_exc()
    
    def run(self):
        try:
            self.bot.run(self.token)
        except discord.LoginFailure:
            print("❌ Invalid token")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            if self.command_handler.scraper:
                asyncio.run(self.command_handler.scraper.cleanup())
        except Exception as e:
            import traceback
            print(f"❌ Fatal: {e}")
            traceback.print_exc()

# ==================== MAIN ====================
if __name__ == "__main__":
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Create temp directory if needed (for screenshots, downloads, etc.)
    os.makedirs("temp", exist_ok=True)
    
    bot = Bot()
    bot.run()
