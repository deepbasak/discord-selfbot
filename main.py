"""
Advanced Discord SelfBot with Selenium Integration
Main entry point
"""

import os
import sys
import asyncio
import time
import discord
from modules.commands import CommandHandler
from modules.utils import load_config


def patch_discord_state():
    """Monkey patch discord.py-self to fix NoneType iteration errors
    
    The issue is in discord/state.py line 1039 where it tries to iterate over
    data.get('pending_payments', []) but the value can be None even if the key exists.
    """
    try:
        # Import state module
        from discord import state as discord_state
        
        # Get the original method
        original_parse_ready_supplemental = discord_state.ConnectionState.parse_ready_supplemental
        
        async def patched_parse_ready_supplemental(self, data):
            """Patched version that handles None values for pending_payments and connected_accounts"""
            # Fix pending_payments - handle None case
            # The issue: data.get('pending_payments', []) returns None if key exists with None value
            pending_payments_raw = data.get('pending_payments')
            pending_payments_data = pending_payments_raw if pending_payments_raw is not None else []
            
            # Use the same logic as original but with safe None handling
            try:
                # Import Payment class from state module
                Payment = getattr(discord_state, 'Payment', None)
                if Payment:
                    self.pending_payments = {int(p['id']): Payment(state=self, data=p) for p in pending_payments_data}
                else:
                    # Fallback if Payment class doesn't exist
                    self.pending_payments = {int(p['id']): p for p in pending_payments_data if p and 'id' in p}
            except (TypeError, KeyError, ValueError) as e:
                print(f"[WARNING] Error processing pending_payments: {e}")
                self.pending_payments = {}
            
            # Fix connected_accounts - handle None case
            connected_accounts_raw = data.get('connected_accounts')
            connected_accounts_data = connected_accounts_raw if connected_accounts_raw is not None else []
            
            try:
                # Import ConnectedAccount class from state module
                ConnectedAccount = getattr(discord_state, 'ConnectedAccount', None)
                if ConnectedAccount:
                    self.connected_accounts = {int(acc['id']): ConnectedAccount(state=self, data=acc) for acc in connected_accounts_data}
                else:
                    # Fallback if ConnectedAccount class doesn't exist
                    self.connected_accounts = {int(acc['id']): acc for acc in connected_accounts_data if acc and 'id' in acc}
            except (TypeError, KeyError, ValueError) as e:
                print(f"[WARNING] Error processing connected_accounts: {e}")
                self.connected_accounts = {}
        
        # Apply the patch
        discord_state.ConnectionState.parse_ready_supplemental = patched_parse_ready_supplemental
    except Exception:
        pass


class AdvancedSelfBot:
    """Main bot class"""
    
    def __init__(self):
        # Apply discord.py-self patches before initializing bot
        patch_discord_state()
        
        self.config = load_config()
        self.token = self.config.get("token", "").strip() if self.config.get("token") else ""
        self.prefix = self.config.get("prefix", "*")
        self.start_time = time.time()
        
        if not self.token or self.token == "YOUR_BOT_TOKEN_HERE" or len(self.token) < 10:
            print("❌ Please set your token in config/config.json")
            sys.exit(1)
        
        # Initialize Discord client (selfbot mode)
        # discord.py-self 2.0.0 doesn't use Intents - it's a selfbot
        self.bot = discord.Client()
        self.command_handler = CommandHandler(self.bot, self.config, self.start_time, self)
        
        self.setup_events()
    
    def setup_events(self):
        """Setup Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            print(f"✅ Bot logged in as {self.bot.user.name}#{self.bot.user.discriminator}")
            print(f"🆔 User ID: {self.bot.user.id}")
            
            # Safely get guild information
            try:
                guilds = self.bot.guilds if hasattr(self.bot, 'guilds') and self.bot.guilds else []
                print(f"📊 Connected to {len(guilds)} servers")
                if guilds:
                    total_members = sum(g.member_count if hasattr(g, 'member_count') and g.member_count else 0 for g in guilds)
                    print(f"👥 Watching {total_members} members")
            except Exception as e:
                print(f"⚠️  Could not fetch server information: {e}")
            
            print("=" * 50)
            
            # Clean temp files on startup
            from modules.utils import clean_temp_files
            clean_temp_files()
        
        @self.bot.event
        async def on_message(message: discord.Message):
            content = message.content
            
            # Quick check: if message doesn't start with prefix, handle non-command features
            if not content.startswith(self.prefix):
                # For selfbots, we ignore non-prefix messages from ourselves to avoid loops
                if message.author.id == self.bot.user.id:
                    return
                # Handle copycat
                if message.author.id in self.command_handler.copycat_users:
                    try:
                        await message.channel.send(content)
                    except:
                        pass
                
                # Handle AFK mentions - check if bot is mentioned and bot is AFK
                if self.bot.user.mentioned_in(message) and self.bot.user.id in self.command_handler.afk_users:
                    afk_msg = self.command_handler.afk_users[self.bot.user.id]
                    try:
                        await message.reply(afk_msg)
                    except:
                        pass
                
                # Handle auto-reply
                autoreply_config = self.config.get("autoreply", {})
                autoreply_enabled = False
                
                if str(message.channel.id) in autoreply_config.get("channels", []):
                    autoreply_enabled = True
                
                if str(message.author.id) in autoreply_config.get("users", []):
                    autoreply_enabled = True
                
                if autoreply_enabled and autoreply_config.get("messages"):
                    import random
                    reply_msg = random.choice(autoreply_config.get("messages", []))
                    try:
                        await message.reply(reply_msg)
                    except:
                        pass
                
                return
            
            # Check for remote user authorization
            # Bot itself can always use commands
            if message.author.id != self.bot.user.id:
                remote_users = self.config.get("remote-users", [])
                if remote_users and str(message.author.id) not in remote_users:
                    # Only allow remote users if list is not empty
                    return
            
            # Parse command
            parts = content[len(self.prefix):].strip().split()
            if not parts:
                return
            
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Execute command
            try:
                result = await self.command_handler.handle_command(message, command, args)
                if result is False:
                    # Command not found
                    await self.command_handler.safe_edit(message, f"❌ Unknown command: `{command}`\nType `{self.prefix}help` for a list of commands.")
            except Exception as e:
                import traceback
                print(f"[DEBUG] Error executing command {command}: {e}")
                traceback.print_exc()
                try:
                    await self.command_handler.safe_edit(message, f"❌ Error: {str(e)}")
                except Exception as e2:
                    print(f"[DEBUG] Failed to send error message: {e2}")
        
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            import traceback
            print(f"❌ Error in event {event}:")
            traceback.print_exc()
    
    def run(self):
        """Run the bot"""
        try:
            self.bot.run(self.token)
        except discord.LoginFailure:
            print("❌ Invalid token. Please check your token in config/config.json")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            try:
                if hasattr(self.command_handler, 'scraper'):
                    asyncio.run(self.command_handler.scraper.cleanup())
            except:
                pass
        except Exception as e:
            import traceback
            print(f"❌ Fatal error: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("config", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("modules", exist_ok=True)
    
    bot = AdvancedSelfBot()
    bot.run()
