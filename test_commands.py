"""
Test script to verify all bot commands are working
Run this script to test all commands with sample inputs
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock
import discord

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.commands import CommandHandler
from modules.utils import load_config


class MockMessage:
    """Mock Discord message for testing"""
    def __init__(self, content, author_id, bot_user_id, channel_id=123456789):
        self.content = content
        self.author = Mock()
        self.author.id = author_id
        self.channel = Mock()
        self.channel.id = channel_id
        self.channel.send = AsyncMock()
        self.mentions = []
        self.guild = None
        self.edit = AsyncMock()
        self.reply = AsyncMock()
        self.delete = AsyncMock()
        
    def mentioned_in(self, message):
        return False


class MockBot:
    """Mock Discord bot for testing"""
    def __init__(self, user_id=930003116127059968):
        self.user = Mock()
        self.user.id = user_id
        self.user.name = "TestBot"
        self.user.discriminator = "0"
        self.latency = 0.05
        self.http = Mock()
        self.http.token = "test_token"
        self.http._HTTPClient__session = None
        self.guilds = []
        self.change_presence = AsyncMock()


async def test_command(command_name, handler, message, args, expected_success=True):
    """Test a single command"""
    try:
        result = await handler.handle_command(message, command_name, args)
        if expected_success:
            print(f"[OK] {command_name:20} - OK")
        else:
            print(f"[WARN] {command_name:20} - Expected failure, got: {result}")
        return True
    except Exception as e:
        if expected_success:
            print(f"[ERROR] {command_name:20} - ERROR: {str(e)[:60]}")
            return False
        else:
            print(f"[OK] {command_name:20} - Expected error occurred")
            return True


async def run_all_tests():
    """Run all command tests"""
    print("=" * 70)
    print("Testing All Bot Commands")
    print("=" * 70)
    print()
    
    # Load config
    config = load_config()
    if not config:
        config = {
            "token": "test_token",
            "prefix": "*",
            "remote-users": [],
            "selenium": {"headless": True}
        }
    
    # Create mock bot and handler
    bot = MockBot()
    start_time = 1234567890.0
    handler = CommandHandler(bot, config, start_time)
    
    bot_user_id = bot.user.id
    test_user_id = 999999999999999999  # Different user for testing
    
    # Test results
    results = {"passed": 0, "failed": 0, "skipped": 0}
    
    # Basic Commands
    print("[Basic] Testing Basic Commands...")
    message = MockMessage("*help", bot_user_id, bot_user_id)
    results["passed" if await test_command("help", handler, message, []) else "failed"] += 1
    
    message = MockMessage("*ping", bot_user_id, bot_user_id)
    results["passed" if await test_command("ping", handler, message, []) else "failed"] += 1
    
    message = MockMessage("*uptime", bot_user_id, bot_user_id)
    results["passed" if await test_command("uptime", handler, message, []) else "failed"] += 1
    
    message = MockMessage("*changeprefix", bot_user_id, bot_user_id)
    results["passed" if await test_command("changeprefix", handler, message, ["!"]) else "failed"] += 1
    
    print()
    
    # Web Utilities
    print("[Web] Testing Web Utilities...")
    message = MockMessage("*pingweb", bot_user_id, bot_user_id)
    results["passed" if await test_command("pingweb", handler, message, ["https://google.com"]) else "failed"] += 1
    
    message = MockMessage("*geoip", bot_user_id, bot_user_id)
    results["passed" if await test_command("geoip", handler, message, ["8.8.8.8"]) else "failed"] += 1
    
    message = MockMessage("*qr", bot_user_id, bot_user_id)
    results["passed" if await test_command("qr", handler, message, ["test"]) else "failed"] += 1
    
    print()
    
    # Message Manipulation
    print("[Message] Testing Message Manipulation...")
    message = MockMessage("*reverse", bot_user_id, bot_user_id)
    results["passed" if await test_command("reverse", handler, message, ["hello"]) else "failed"] += 1
    
    message = MockMessage("*edit", bot_user_id, bot_user_id)
    results["passed" if await test_command("edit", handler, message, ["test message"]) else "failed"] += 1
    
    message = MockMessage("*hidemention", bot_user_id, bot_user_id)
    results["passed" if await test_command("hidemention", handler, message, ["@user"]) else "failed"] += 1
    
    print()
    
    # Fun Commands
    print("[Fun] Testing Fun Commands...")
    message = MockMessage("*gentoken", bot_user_id, bot_user_id)
    results["passed" if await test_command("gentoken", handler, message, []) else "failed"] += 1
    
    message = MockMessage("*nitro", bot_user_id, bot_user_id)
    results["passed" if await test_command("nitro", handler, message, []) else "failed"] += 1
    
    message = MockMessage("*ascii", bot_user_id, bot_user_id)
    results["passed" if await test_command("ascii", handler, message, ["test"]) else "failed"] += 1
    
    message = MockMessage("*minesweeper", bot_user_id, bot_user_id)
    results["passed" if await test_command("minesweeper", handler, message, ["9", "9"]) else "failed"] += 1
    
    message = MockMessage("*leetpeek", bot_user_id, bot_user_id)
    results["passed" if await test_command("leetpeek", handler, message, ["hello"]) else "failed"] += 1
    
    message = MockMessage("*hypesquad", bot_user_id, bot_user_id)
    results["passed" if await test_command("hypesquad", handler, message, ["bravery"]) else "failed"] += 1
    
    print()
    
    # Automation Commands
    print("[Automation] Testing Automation Commands...")
    message = MockMessage("*afk", bot_user_id, bot_user_id)
    results["passed" if await test_command("afk", handler, message, ["on", "test"]) else "failed"] += 1
    
    message = MockMessage("*autoreply", bot_user_id, bot_user_id)
    results["passed" if await test_command("autoreply", handler, message, ["on"]) else "failed"] += 1
    
    print()
    
    # Activities
    print("[Activities] Testing Activity Commands...")
    message = MockMessage("*playing", bot_user_id, bot_user_id)
    results["passed" if await test_command("playing", handler, message, ["test game"]) else "failed"] += 1
    
    message = MockMessage("*watching", bot_user_id, bot_user_id)
    results["passed" if await test_command("watching", handler, message, ["test video"]) else "failed"] += 1
    
    message = MockMessage("*stopactivity", bot_user_id, bot_user_id)
    results["passed" if await test_command("stopactivity", handler, message, []) else "failed"] += 1
    
    print()
    
    # Commands that require Discord connection (will fail but test structure)
    print("[Discord] Testing Discord-Dependent Commands (may fail without real connection)...")
    message = MockMessage("*guildinfo", bot_user_id, bot_user_id)
    message.guild = Mock()
    message.guild.name = "Test Guild"
    message.guild.id = 123456789
    message.guild.owner = None
    message.guild.member_count = 100
    message.guild.created_at = Mock()
    message.guild.created_at.strftime = lambda fmt: "2024-01-01 00:00:00"
    message.guild.channels = []
    message.guild.roles = []
    results["skipped"] += 1  # Skip guild commands as they need real guild
    
    print()
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"[PASS] Passed:  {results['passed']}")
    print(f"[FAIL] Failed:  {results['failed']}")
    print(f"[SKIP] Skipped: {results['skipped']}")
    print("=" * 70)
    
    # Cleanup
    try:
        await handler.scraper.cleanup()
    except:
        pass


if __name__ == "__main__":
    print("Starting command tests...")
    print("Note: Some commands require Discord connection and will be skipped")
    print()
    asyncio.run(run_all_tests())

