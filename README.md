# Discord SelfBot

Simple Discord selfbot in a single file - ready for Replit and local use.

## Quick Start

1. Open `main.py`
2. Find the `TOKEN` variable at the top (line ~7)
3. Replace `"YOUR_TOKEN_HERE"` with your Discord token:
   ```python
   TOKEN = "your_actual_discord_token_here"
   ```
4. Run `python main.py`

**Note:** The bot auto-installs missing packages on first run!

### Optional: Environment Variable (Replit)
You can also use `TOKEN` environment variable if you prefer.

## Commands

- `*help` - Show all commands
- `*ping` - Check latency
- `*uptime` - Bot uptime
- `*purge <amount>` - Delete messages
- `*screenshot <url>` - Screenshot website
- `*guildinfo` - Server info
- `*playing <status>` - Set status
- And many more! Type `*help` for full list.

## Requirements

- Python 3.8+
- `discord.py-self==2.0.0`
- Optional: Selenium for web features

## Installation

```bash
pip install -r requirements.txt
```

## Note

This is a selfbot - it automates your personal Discord account. Use responsibly.
