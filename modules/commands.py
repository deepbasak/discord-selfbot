"""
Command handlers for the Discord selfbot
"""

import os
import sys
import asyncio
import time
import re
import random
from typing import Optional, List
import discord
import aiohttp
from modules.selenium_scraper import SeleniumScraper
from modules.utils import (
    load_config, save_config, get_uptime, ping_website,
    geoip_lookup, generate_qr_code, reverse_text, generate_fake_token,
    create_temp_dir, clean_temp_files
)
import requests
from datetime import datetime


class CommandHandler:
    """Handles all bot commands"""
    
    def __init__(self, bot, config, start_time, bot_instance=None):
        self.bot = bot
        self.config = config
        self.start_time = start_time
        self.bot_instance = bot_instance  # Reference to AdvancedSelfBot instance
        self.scraper = SeleniumScraper(config)
        self.afk_users = {}
        self.copycat_users = set()
        
        # Build command routing dictionary for O(1) lookup instead of O(n) if/elif chain
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
            "test": self.cmd_test, "testcommands": self.cmd_test,
        }
    
    async def _delete_after(self, message, delay):
        """Helper to delete a message after a delay"""
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except:
            pass
    
    async def safe_edit(self, message: discord.Message, content: str):
        """Safely edit a message, or send new message if edit fails or if message is from another user"""
        # If message is from bot itself, edit directly (faster)
        if message.author.id == self.bot.user.id:
            try:
                await message.edit(content=content)
            except:
                # If edit fails, send new message
                try:
                    await message.channel.send(content)
                except:
                    pass
        else:
            # Message is from another user, send new message instead
            try:
                await message.channel.send(content)
            except:
                pass
        
    async def handle_command(self, message: discord.Message, command: str, args: List[str]):
        """Route commands to appropriate handlers - optimized with dictionary lookup"""
        command = command.lower()
        
        # Fast O(1) dictionary lookup instead of O(n) if/elif chain
        handler = self.command_map.get(command)
        if handler:
            # Commands that don't need args
            if command in ("shutdown", "uptime", "ping", "guildinfo", "guildicon", 
                          "guildbanner", "fetchmembers", "stopactivity", "gentoken", 
                          "nitro", "firstmessage", "test", "testcommands"):
                await handler(message)
            else:
                await handler(message, args)
            return True
        
        return False
    
    async def cmd_help(self, message: discord.Message, args: List[str]):
        """Show help menu"""
        prefix = self.config.get("prefix", "*")
        help_text = f"""```yaml
╔══════════════════════════════════════════════════════════╗
║           Advanced Discord SelfBot - Commands            ║
╚══════════════════════════════════════════════════════════╝

[Basic]
{prefix}help - Show this help menu
{prefix}ping - Check bot latency
{prefix}uptime - Show bot uptime
{prefix}changeprefix <prefix> - Change command prefix
{prefix}shutdown - Stop the bot

[User Management]
{prefix}remoteuser ADD|REMOVE <@user> - Manage remote users
{prefix}copycat ON|OFF <@user> - Copy user messages

[Web Utilities]
{prefix}pingweb <url> - Ping a website
{prefix}geoip <ip> - Lookup IP geolocation
{prefix}qr <text> - Generate QR code
{prefix}screenshot <url> - Take website screenshot
{prefix}scrape <url> - Scrape website content
{prefix}download <url> - Download file from URL

[Message Manipulation]
{prefix}reverse <text> - Reverse text
{prefix}edit <text> - Move edit tag position
{prefix}hidemention <text> - Hide mentions

[Server Management]
{prefix}purge <amount> - Delete messages
{prefix}clear - Clear channel messages
{prefix}cleardm <amount> - Clear DMs
{prefix}guildinfo - Get server info
{prefix}guildicon - Get server icon
{prefix}guildbanner - Get server banner
{prefix}guildrename <name> - Rename server
{prefix}usericon <@user> - Get user avatar

[Automation]
{prefix}spam <amount> <message> - Spam messages
{prefix}quickdelete <message> - Send and delete message
{prefix}autoreply ON|OFF - Toggle auto-reply
{prefix}afk ON|OFF [message] - Set AFK status

[Messaging]
{prefix}dmall <message> - DM all members
{prefix}sendall <message> - Send to all channels
{prefix}fetchmembers - Get all server members
{prefix}firstmessage - Get first message link

[Activities]
{prefix}playing <status> - Set playing status
{prefix}watching <status> - Set watching status
{prefix}stopactivity - Clear activity

[Fun]
{prefix}gentoken - Generate fake token
{prefix}hypesquad <house> - Change HypeSquad badge
{prefix}nitro - Generate fake nitro code
{prefix}ascii <text> - ASCII art
{prefix}minesweeper <width> <height> - Play minesweeper
{prefix}leetpeek <text> - Leet speak

[Webhooks]
{prefix}whremove <webhook_url> - Delete webhook

[Testing]
{prefix}test - Run command tests (verifies all commands work)
```"""
        await self.safe_edit(message, help_text)
    
    async def cmd_shutdown(self, message: discord.Message):
        """Shutdown the bot"""
        await self.safe_edit(message, "🛑 Shutting down...")
        await self.scraper.cleanup()
        await self.bot.close()
    
    async def cmd_uptime(self, message: discord.Message):
        """Show bot uptime"""
        uptime = get_uptime(self.start_time)
        await self.safe_edit(message, f"⏱️ Uptime: {uptime}")
    
    async def cmd_ping(self, message: discord.Message):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000, 2)
        await self.safe_edit(message, f"🏓 Pong! Latency: {latency}ms")
    
    async def cmd_changeprefix(self, message: discord.Message, args: List[str]):
        """Change command prefix"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a prefix")
            return
        
        new_prefix = args[0]
        self.config["prefix"] = new_prefix
        save_config(self.config)
        
        # Update prefix in bot instance if available (works immediately, no restart needed)
        if self.bot_instance:
            self.bot_instance.prefix = new_prefix
        
        await self.safe_edit(message, f"✅ Prefix changed to: `{new_prefix}`\n💡 The new prefix is now active!")
    
    async def cmd_remoteuser(self, message: discord.Message, args: List[str]):
        """Manage remote users"""
        if len(args) < 2:
            await self.safe_edit(message, "❌ Usage: `remoteuser ADD|REMOVE <@user>`")
            return
        
        action = args[0].upper()
        remote_users = self.config.get("remote-users", [])
        
        for user in message.mentions:
            user_id = str(user.id)
            if action == "ADD":
                if user_id not in remote_users:
                    remote_users.append(user_id)
                    await self.safe_edit(message, f"✅ Added {user.mention} to remote users")
                else:
                    await self.safe_edit(message, f"⚠️ {user.mention} is already a remote user")
            elif action == "REMOVE":
                if user_id in remote_users:
                    remote_users.remove(user_id)
                    await self.safe_edit(message, f"✅ Removed {user.mention} from remote users")
                else:
                    await self.safe_edit(message, f"⚠️ {user.mention} is not a remote user")
        
        self.config["remote-users"] = remote_users
        save_config(self.config)
    
    async def cmd_copycat(self, message: discord.Message, args: List[str]):
        """Toggle copycat mode for a user"""
        if len(args) < 2:
            await self.safe_edit(message, "❌ Usage: `copycat ON|OFF <@user>`")
            return
        
        mode = args[0].upper()
        if not message.mentions:
            await self.safe_edit(message, "❌ Please mention a user")
            return
        
        user_id = message.mentions[0].id
        if mode == "ON":
            self.copycat_users.add(user_id)
            await self.safe_edit(message, f"✅ Copycat enabled for {message.mentions[0].mention}")
        elif mode == "OFF":
            self.copycat_users.discard(user_id)
            await self.safe_edit(message, f"✅ Copycat disabled for {message.mentions[0].mention}")
    
    async def cmd_pingweb(self, message: discord.Message, args: List[str]):
        """Ping a website"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a URL")
            return
        
        url = args[0]
        result = ping_website(url)
        
        if result.get("online"):
            await self.safe_edit(message, f"🌐 {url}\n✅ Status: {result['status_code']}\n⏱️ Response Time: {result['response_time']}")
        else:
            await self.safe_edit(message, f"❌ {url} is offline or unreachable")
    
    async def cmd_geoip(self, message: discord.Message, args: List[str]):
        """Lookup IP geolocation"""
        if not args:
            await self.safe_edit(message, "❌ Please provide an IP address")
            return
        
        ip = args[0]
        result = geoip_lookup(ip)
        
        if "error" in result:
            await self.safe_edit(message, f"❌ Error: {result['error']}")
        else:
            info = f"""🌍 IP: {ip}
📍 Country: {result.get('country', 'N/A')}
🏙️ City: {result.get('city', 'N/A')}
🌐 ISP: {result.get('isp', 'N/A')}
⏰ Timezone: {result.get('timezone', 'N/A')}"""
            await self.safe_edit(message, info)
    
    async def cmd_qr(self, message: discord.Message, args: List[str]):
        """Generate QR code"""
        if not args:
            await self.safe_edit(message, "❌ Please provide text to encode")
            return
        
        text = " ".join(args)
        qr_img = generate_qr_code(text)
        
        await self.safe_edit(message, "📱 QR Code Generated:")
        await message.channel.send(file=discord.File(qr_img, filename="qrcode.png"))
    
    async def cmd_reverse(self, message: discord.Message, args: List[str]):
        """Reverse text"""
        if not args:
            await self.safe_edit(message, "❌ Please provide text to reverse")
            return
        
        text = " ".join(args)
        reversed_text = reverse_text(text)
        await self.safe_edit(message, reversed_text)
    
    async def cmd_edit(self, message: discord.Message, args: List[str]):
        """Move edit tag position"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a message")
            return
        
        text = " ".join(args)
        await self.safe_edit(message, f"{text} (edited)")
    
    async def cmd_hidemention(self, message: discord.Message, args: List[str]):
        """Hide mentions in message"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a message")
            return
        
        text = " ".join(args)
        # Hide mentions using zero-width spaces
        hidden = text.replace("@", "@\u200b")
        await self.safe_edit(message, hidden)
    
    async def cmd_tts(self, message: discord.Message, args: List[str]):
        """Generate text-to-speech using Selenium"""
        if not args:
            await self.safe_edit(message, "❌ Please provide text to convert")
            return
        
        text = " ".join(args)
        await self.safe_edit(message, "🔊 Generating TTS audio... This may take a moment.")
        
        # Try primary TTS service
        audio_url = await self.scraper.text_to_speech_elevenlabs(text)
        
        if not audio_url:
            # Try alternative service
            audio_url = await self.scraper.text_to_speech_alternative(text)
        
        if audio_url:
            try:
                # Download audio file
                response = requests.get(audio_url, timeout=30)
                temp_dir = create_temp_dir()
                filename = f"tts_{int(time.time())}.mp3"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                await self.safe_edit(message, "🔊 TTS Audio Generated:")
                await message.channel.send(file=discord.File(filepath))
                
                # Clean up after sending
                await asyncio.sleep(5)
                try:
                    os.remove(filepath)
                except:
                    pass
            except Exception as e:
                await self.safe_edit(message, f"❌ Error downloading audio: {str(e)}")
        else:
            await self.safe_edit(message, "❌ Failed to generate TTS audio. Please try again.")
    
    async def cmd_screenshot(self, message: discord.Message, args: List[str]):
        """Take a screenshot of a website"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a URL")
            return
        
        url = args[0]
        await self.safe_edit(message, "📸 Taking screenshot...")
        
        temp_dir = create_temp_dir()
        filename = f"screenshot_{int(time.time())}.png"
        filepath = os.path.join(temp_dir, filename)
        
        screenshot_path = await self.scraper.take_screenshot(url, filepath)
        
        if screenshot_path and os.path.exists(screenshot_path):
            await self.safe_edit(message, f"📸 Screenshot of {url}:")
            await message.channel.send(file=discord.File(screenshot_path))
            await asyncio.sleep(5)
            try:
                os.remove(screenshot_path)
            except:
                pass
        else:
            await self.safe_edit(message, "❌ Failed to take screenshot")
    
    async def cmd_scrape(self, message: discord.Message, args: List[str]):
        """Scrape website content"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a URL")
            return
        
        url = args[0]
        await self.safe_edit(message, "🔍 Scraping website...")
        
        # Default selectors - can be customized
        selectors = {
            "title": "title",
            "content": "body"
        }
        
        result = await self.scraper.scrape_website_content(url, selectors)
        
        if result:
            content = f"📄 Scraped Content from {url}:\n\n"
            for key, value in result.items():
                if value:
                    content += f"**{key.capitalize()}**: {value[:500]}...\n\n"
            await self.safe_edit(message, content[:2000])
        else:
            await self.safe_edit(message, "❌ Failed to scrape website")
    
    async def cmd_download(self, message: discord.Message, args: List[str]):
        """Download file from URL"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a URL")
            return
        
        url = args[0]
        await self.safe_edit(message, "⬇️ Downloading file...")
        
        temp_dir = create_temp_dir()
        filename = f"download_{int(time.time())}"
        filepath = os.path.join(temp_dir, filename)
        
        downloaded = await self.scraper.download_file(url, filepath)
        
        if downloaded and os.path.exists(downloaded):
            await self.safe_edit(message, "⬇️ File downloaded:")
            await message.channel.send(file=discord.File(downloaded))
            await asyncio.sleep(5)
            try:
                os.remove(downloaded)
            except:
                pass
        else:
            await self.safe_edit(message, "❌ Failed to download file")
    
    async def cmd_purge(self, message: discord.Message, args: List[str]):
        """Delete messages"""
        if not args:
            await self.safe_edit(message, "❌ Please provide amount")
            return
        
        try:
            amount = int(args[0])
            if amount <= 0:
                await self.safe_edit(message, "❌ Amount must be greater than 0")
                return
            
            # Delete the command message first, then purge the rest
            try:
                await message.delete()
            except:
                pass
            
            # Purge the specified amount (we already deleted the command message)
            deleted = await message.channel.purge(limit=amount)
            deleted_count = len(deleted) + 1  # +1 for the command message we deleted
            
            confirmation = await message.channel.send(f"✅ Deleted {deleted_count} messages")
            # Delete confirmation in background (non-blocking)
            asyncio.create_task(self._delete_after(confirmation, 3))
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_clear(self, message: discord.Message, args: List[str]):
        """Clear channel messages"""
        # Use provided amount or default to 100
        if args:
            try:
                amount = int(args[0])
                await self.cmd_purge(message, [str(amount)])
            except ValueError:
                await self.safe_edit(message, "❌ Please provide a valid number")
        else:
            await self.cmd_purge(message, ["100"])
    
    async def cmd_cleardm(self, message: discord.Message, args: List[str]):
        """Clear DMs"""
        if not args:
            await self.safe_edit(message, "❌ Please provide amount")
            return
        
        try:
            amount = int(args[0]) + 1
            if isinstance(message.channel, discord.DMChannel):
                deleted = await message.channel.purge(limit=amount)
                await message.channel.send(f"✅ Deleted {len(deleted)} messages")
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_spam(self, message: discord.Message, args: List[str]):
        """Spam messages"""
        if len(args) < 2:
            await self.safe_edit(message, "❌ Usage: `spam <amount> <message>`")
            return
        
        try:
            amount = int(args[0])
            spam_text = " ".join(args[1:])
            
            for _ in range(min(amount, 20)):  # Limit to 20 for safety
                await message.channel.send(spam_text)
                await asyncio.sleep(0.5)
            
            await message.delete()
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_quickdelete(self, message: discord.Message, args: List[str]):
        """Send and delete message after 2 seconds"""
        if not args:
            await self.safe_edit(message, "❌ Please provide a message")
            return
        
        text = " ".join(args)
        sent = await message.channel.send(text)
        await message.delete()
        await asyncio.sleep(2)
        await sent.delete()
    
    async def cmd_autoreply(self, message: discord.Message, args: List[str]):
        """Toggle auto-reply"""
        if not args:
            await self.safe_edit(message, "❌ Usage: `autoreply ON|OFF`")
            return
        
        mode = args[0].upper()
        await self.safe_edit(message, f"✅ Auto-reply: {mode}")
    
    async def cmd_afk(self, message: discord.Message, args: List[str]):
        """Set AFK status"""
        if not args:
            await self.safe_edit(message, "❌ Usage: `afk ON|OFF [message]`")
            return
        
        mode = args[0].upper()
        afk_message = " ".join(args[1:]) if len(args) > 1 else self.config.get("afk", {}).get("message", "I am AFK")
        
        # Store AFK status for the bot's user ID, not the message author
        bot_user_id = self.bot.user.id
        
        if mode == "ON":
            self.afk_users[bot_user_id] = afk_message
            await self.safe_edit(message, f"✅ AFK mode enabled: {afk_message}")
        elif mode == "OFF":
            self.afk_users.pop(bot_user_id, None)
            await self.safe_edit(message, "✅ AFK mode disabled")
    
    async def cmd_guildinfo(self, message: discord.Message):
        """Get server info"""
        if not message.guild:
            await self.safe_edit(message, "❌ This command only works in servers")
            return
        
        guild = message.guild
        info = f"""📊 Server Info: {guild.name}
🆔 ID: {guild.id}
👑 Owner: {guild.owner.mention if guild.owner else 'N/A'}
👥 Members: {guild.member_count}
📅 Created: {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}
📁 Channels: {len(guild.channels)}
🎭 Roles: {len(guild.roles)}"""
        await self.safe_edit(message, info)
    
    async def cmd_guildicon(self, message: discord.Message):
        """Get server icon"""
        if not message.guild or not message.guild.icon:
            await self.safe_edit(message, "❌ Server has no icon")
            return
        
        await self.safe_edit(message, f"🖼️ Server Icon: {message.guild.icon.url}")
    
    async def cmd_guildbanner(self, message: discord.Message):
        """Get server banner"""
        if not message.guild or not message.guild.banner:
            await self.safe_edit(message, "❌ Server has no banner")
            return
        
        await self.safe_edit(message, f"🎨 Server Banner: {message.guild.banner.url}")
    
    async def cmd_guildrename(self, message: discord.Message, args: List[str]):
        """Rename server"""
        if not message.guild:
            await self.safe_edit(message, "❌ This command only works in servers")
            return
        
        if not args:
            await self.safe_edit(message, "❌ Please provide a new name")
            return
        
        new_name = " ".join(args)
        try:
            await message.guild.edit(name=new_name)
            await self.safe_edit(message, f"✅ Server renamed to: {new_name}")
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_fetchmembers(self, message: discord.Message):
        """Fetch all server members"""
        if not message.guild:
            await self.safe_edit(message, "❌ This command only works in servers")
            return
        
        members = [str(m) for m in message.guild.members]
        member_list = "\n".join(members[:50])  # Limit to 50
        await self.safe_edit(message, f"👥 Members ({len(members)}):\n{member_list}")
    
    async def cmd_usericon(self, message: discord.Message, args: List[str]):
        """Get user avatar"""
        if not message.mentions:
            user = message.author
        else:
            user = message.mentions[0]
        
        await self.safe_edit(message, f"🖼️ {user.name}'s Avatar: {user.avatar.url if user.avatar else 'No avatar'}")
    
    async def cmd_dmall(self, message: discord.Message, args: List[str]):
        """DM all members"""
        if not message.guild:
            await self.safe_edit(message, "❌ This command only works in servers")
            return
        
        if not args:
            await self.safe_edit(message, "❌ Please provide a message")
            return
        
        text = " ".join(args)
        count = 0
        
        for member in message.guild.members:
            if member.id != self.bot.user.id:
                try:
                    await member.send(text)
                    count += 1
                    await asyncio.sleep(1)  # Rate limit
                except:
                    pass
        
        await self.safe_edit(message, f"✅ Sent DM to {count} members")
    
    async def cmd_sendall(self, message: discord.Message, args: List[str]):
        """Send message to all channels"""
        if not message.guild:
            await self.safe_edit(message, "❌ This command only works in servers")
            return
        
        if not args:
            await self.safe_edit(message, "❌ Please provide a message")
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
        
        await self.safe_edit(message, f"✅ Sent message to {count} channels")
    
    async def cmd_playing(self, message: discord.Message, args: List[str]):
        """Set playing status"""
        if not args:
            await self.safe_edit(message, "❌ Please provide status text")
            return
        
        status = " ".join(args)
        activity = discord.Game(name=status)
        await self.bot.change_presence(activity=activity)
        await self.safe_edit(message, f"✅ Playing status set to: {status}")
    
    async def cmd_watching(self, message: discord.Message, args: List[str]):
        """Set watching status"""
        if not args:
            await self.safe_edit(message, "❌ Please provide status text")
            return
        
        status = " ".join(args)
        activity = discord.Activity(type=discord.ActivityType.watching, name=status)
        await self.bot.change_presence(activity=activity)
        await self.safe_edit(message, f"✅ Watching status set to: {status}")
    
    async def cmd_stopactivity(self, message: discord.Message):
        """Clear activity"""
        await self.bot.change_presence(activity=None)
        await self.safe_edit(message, "✅ Activity cleared")
    
    async def cmd_gentoken(self, message: discord.Message):
        """Generate fake token"""
        token = generate_fake_token()
        await self.safe_edit(message, f"🎫 Generated Token: `{token}`")
    
    async def cmd_hypesquad(self, message: discord.Message, args: List[str]):
        """Change HypeSquad badge"""
        if not args:
            await self.safe_edit(message, "❌ Usage: `hypesquad <house>`\nHouses: bravery, brilliance, balance")
            return
        
        house = args[0].lower()
        houses = {
            "bravery": 1,
            "brilliance": 2,
            "balance": 3
        }
        
        if house not in houses:
            await self.safe_edit(message, "❌ Invalid house. Choose: bravery, brilliance, balance")
            return
        
        house_id = houses[house]
        
        try:
            # Get token from bot's HTTP client
            token = self.bot.http.token if hasattr(self.bot.http, 'token') else self.config.get("token")
            
            # Make API request to change HypeSquad house
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # Discord API endpoint for HypeSquad house
            url = "https://discord.com/api/v9/hypesquad/online"
            payload = {"house_id": house_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 204:
                        await self.safe_edit(message, f"✅ HypeSquad house set to: {house.capitalize()}")
                    else:
                        error_text = await response.text()
                        await self.safe_edit(message, f"❌ Failed to set HypeSquad house. Status: {response.status}\nError: {error_text[:200]}")
        except Exception as e:
            await self.safe_edit(message, f"❌ Error changing HypeSquad badge: {str(e)}")
    
    async def cmd_nitro(self, message: discord.Message):
        """Generate fake nitro code"""
        code = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(16)])
        await self.safe_edit(message, f"🎁 Discord Nitro: https://discord.gift/{code}")
    
    async def cmd_ascii(self, message: discord.Message, args: List[str]):
        """Convert to ASCII art"""
        if not args:
            await self.safe_edit(message, "❌ Please provide text")
            return
        
        text = " ".join(args)
        # Simple ASCII conversion (can be enhanced with pyfiglet)
        ascii_text = "\n".join([char.upper() for char in text])
        await self.safe_edit(message, f"```\n{ascii_text}\n```")
    
    async def cmd_minesweeper(self, message: discord.Message, args: List[str]):
        """Play minesweeper"""
        try:
            width = int(args[0]) if args else 9
            height = int(args[1]) if len(args) > 1 else 9
            
            width = min(max(width, 2), 15)
            height = min(max(height, 2), 15)
            
            # Generate minesweeper grid (simplified)
            grid = [[":zero:" for _ in range(width)] for _ in range(height)]
            grid_text = "\n".join(["".join(row) for row in grid])
            
            await self.safe_edit(message, grid_text[:2000])
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_leetpeek(self, message: discord.Message, args: List[str]):
        """Leet speak conversion"""
        if not args:
            await self.safe_edit(message, "❌ Please provide text")
            return
        
        text = " ".join(args)
        leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0',
            's': '5', 't': '7', 'l': '1', 'g': '9'
        }
        
        leet_text = "".join([leet_map.get(char.lower(), char) for char in text])
        await self.safe_edit(message, leet_text)
    
    async def cmd_whremove(self, message: discord.Message, args: List[str]):
        """Remove webhook"""
        if not args:
            await self.safe_edit(message, "❌ Please provide webhook URL")
            return
        
        webhook_url = args[0]
        try:
            webhook = discord.Webhook.from_url(webhook_url, session=self.bot.http._HTTPClient__session)
            await webhook.delete()
            await self.safe_edit(message, "✅ Webhook deleted")
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_firstmessage(self, message: discord.Message):
        """Get first message in channel"""
        try:
            async for msg in message.channel.history(limit=1, oldest_first=True):
                await self.safe_edit(message, f"📌 First Message: {msg.jump_url}")
                break
        except Exception as e:
            await self.safe_edit(message, f"❌ Error: {str(e)}")
    
    async def cmd_test(self, message: discord.Message):
        """Test all commands (runs test_commands.py)"""
        import subprocess
        import sys
        
        await self.safe_edit(message, "🧪 Running command tests... This may take a moment.")
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, "test_commands.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Format output for Discord (limit to 2000 chars)
            if len(output) > 1900:
                output = output[:1900] + "\n... (truncated)"
            
            await self.safe_edit(message, f"```\n{output}\n```")
        except subprocess.TimeoutExpired:
            await self.safe_edit(message, "❌ Test timed out after 30 seconds")
        except Exception as e:
            await self.safe_edit(message, f"❌ Error running tests: {str(e)}")
