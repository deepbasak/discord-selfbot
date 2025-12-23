# Advanced Discord SelfBot with Selenium Integration

An advanced Discord selfbot built with Python that integrates Selenium for web automation and scraping capabilities. This bot can perform heavy tasks like text-to-speech generation, website scraping, screenshots, and much more.

## ⚠️ Important Disclaimer

**This is a selfbot, which means it automates your personal Discord account. Using selfbots violates Discord's Terms of Service and may result in your account being banned. Use at your own risk.**

## 🚀 Features

### Basic Commands
- **Help System**: Comprehensive command documentation
- **Ping**: Check bot latency
- **Uptime**: Monitor how long the bot has been running
- **Prefix Management**: Customize command prefix

### Advanced Selenium Integration
- **Text-to-Speech (TTS)**: Generate audio from text using online TTS services (ElevenLabs, Speechify, etc.)
- **Website Screenshots**: Capture screenshots of any website
- **Web Scraping**: Extract content from websites with custom selectors
- **File Downloads**: Automatically download files from URLs
- **Form Automation**: Fill and submit forms on websites

### Web Utilities
- **Website Pinging**: Check website status and response time
- **IP Geolocation**: Lookup IP address information
- **QR Code Generation**: Create QR codes from text

### Message Manipulation
- **Message Reversal**: Reverse text characters
- **Hidden Mentions**: Hide @mentions in messages
- **Edit Tag Movement**: Manipulate Discord's edit tags

### Server Management
- **Message Purge**: Delete multiple messages
- **Server Info**: Get detailed server information
- **Member Fetching**: Retrieve all server members
- **Channel Broadcasting**: Send messages to all channels
- **DM Mass Messaging**: Send DMs to all server members

### Automation Features
- **Auto-Reply**: Automatic responses in channels or to specific users
- **AFK Mode**: Set away status with custom messages
- **Copycat**: Automatically repeat messages from specific users
- **Spam**: Send multiple messages (rate-limited for safety)

### Activity Management
- **Custom Status**: Set playing/watching status
- **Activity Control**: Clear activities

### Fun Commands
- **ASCII Art**: Convert text to ASCII
- **Minesweeper**: Play minesweeper in Discord
- **Leet Speak**: Convert text to leet speak
- **Fake Token/Nitro**: Generate fake but formatted tokens

## 📋 Requirements

- Python 3.8 or higher
- Chrome/Chromium browser (for Selenium)
- Discord account token

## 🔧 Installation

### Automated Installation

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
python setup.py
```

### Manual Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd discord-selfbot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the bot:**
   - Edit `config/config.json`
   - Add your Discord token
   - Customize settings as needed

4. **Run the bot:**
```bash
python main.py
```

## ⚙️ Configuration

Edit `config/config.json`:

```json
{
  "token": "YOUR_DISCORD_TOKEN_HERE",
  "prefix": "*",
  "remote-users": [],
  "autoreply": {
    "messages": ["Auto-reply message"],
    "channels": [],
    "users": []
  },
  "afk": {
    "enabled": false,
    "message": "I am currently AFK!"
  },
  "copycat": {
    "users": []
  },
  "selenium": {
    "headless": false,
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "window_size": {
      "width": 1920,
      "height": 1080
    }
  },
  "tts": {
    "provider": "elevenlabs",
    "default_voice": "default",
    "save_path": "temp/tts"
  }
}
```

### Getting Your Discord Token

1. Open Discord in your browser
2. Press `F12` to open Developer Tools
3. Go to the `Network` tab
4. Reload the page
5. Find any request to `discord.com`
6. Go to the `Headers` tab
7. Look for `Authorization` header
8. Copy the token value

## 📚 Command Reference

### Basic Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `help` | Show help menu | `*help` |
| `ping` | Check latency | `*ping` |
| `uptime` | Show uptime | `*uptime` |
| `changeprefix` | Change prefix | `*changeprefix !` |
| `shutdown` | Stop bot | `*shutdown` |

### Selenium Commands (Advanced)
| Command | Description | Usage |
|---------|-------------|-------|
| `tts` | Generate TTS audio | `*tts Hello world` |
| `screenshot` | Take website screenshot | `*screenshot https://example.com` |
| `scrape` | Scrape website content | `*scrape https://example.com` |
| `download` | Download file from URL | `*download https://example.com/file.pdf` |

### Web Utilities
| Command | Description | Usage |
|---------|-------------|-------|
| `pingweb` | Ping website | `*pingweb google.com` |
| `geoip` | IP lookup | `*geoip 8.8.8.8` |
| `qr` | Generate QR code | `*qr Hello` |

### Server Management
| Command | Description | Usage |
|---------|-------------|-------|
| `purge` | Delete messages | `*purge 10` |
| `guildinfo` | Server info | `*guildinfo` |
| `guildicon` | Server icon | `*guildicon` |
| `dmall` | DM all members | `*dmall Hello everyone` |
| `sendall` | Send to all channels | `*sendall Announcement` |

### Automation
| Command | Description | Usage |
|---------|-------------|-------|
| `autoreply` | Toggle auto-reply | `*autoreply ON` |
| `afk` | Set AFK status | `*afk ON I'm away` |
| `copycat` | Copy user messages | `*copycat ON @user` |
| `spam` | Spam messages | `*spam 5 Hello` |

## 🔒 Remote User System

Add user IDs to `remote-users` in config to allow remote command execution:

```json
"remote-users": ["USER_ID_1", "USER_ID_2"]
```

Or use the command:
```
*remoteuser ADD @user
```

## 🤖 Selenium Features

### Text-to-Speech
The bot can generate TTS audio using multiple services:
- **ElevenLabs**: High-quality TTS
- **Speechify**: Alternative TTS service
- Automatically downloads and sends audio files

### Web Scraping
- Custom selector support
- Multiple element extraction
- Formatted output

### Screenshots
- Full-page screenshots
- Custom resolution support
- Automatic cleanup

## 📁 Project Structure

```
discord-selfbot/
├── main.py                 # Main bot entry point
├── config/
│   └── config.json        # Configuration file
├── modules/
│   ├── __init__.py
│   ├── commands.py        # Command handlers
│   ├── selenium_scraper.py # Selenium automation
│   └── utils.py           # Utility functions
├── temp/                   # Temporary files
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
├── setup.bat              # Windows setup
└── README.md              # This file
```

## ⚠️ Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver errors:
1. Ensure Chrome is installed
2. The bot uses `webdriver-manager` to auto-install drivers
3. For manual setup, download from [ChromeDriver](https://chromedriver.chromium.org/)

### Selenium Timeout Errors
- Increase `page_load_timeout` in config
- Check your internet connection
- Some websites may block automation

### Discord Login Errors
- Verify your token is correct
- Check if your account is enabled
- Ensure you're using the correct token format

## 🛡️ Security Notes

- **Never share your token** - Keep it secure
- **Don't commit config.json** - It's in `.gitignore`
- **Use remote-users** - Restrict command access
- **Rate limiting** - Built-in rate limiting to prevent spam

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Credits

Inspired by [AstraaDev/selfbot.py](https://github.com/AstraaDev/selfbot.py)

## ⚖️ Legal Notice

This software is provided for educational purposes only. The authors are not responsible for any misuse or damage caused by this software. Using selfbots violates Discord's Terms of Service and may result in account termination.

## 🔄 Updates

For updates and new features, check the repository regularly.

---

**Use responsibly and at your own risk.**
