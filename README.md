# Discord SelfBot

Simple Discord selfbot in a single file - ready for Replit and local use.

## Quick Start

### Replit
1. Fork this repo to Replit
2. Set environment variable: `TOKEN` = your Discord token
3. Run `python main.py`

### Local
1. Create `config/config.json`:
```json
{
  "token": "YOUR_TOKEN_HERE",
  "prefix": "*"
}
```
2. Run `python main.py`

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
