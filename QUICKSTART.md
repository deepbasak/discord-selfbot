# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
python setup.py
```

Or manually:
```bash
pip install -r requirements.txt
```

### Step 2: Configure

1. Copy the example config:
```bash
cp config/config.json.example config/config.json
```

2. Edit `config/config.json`:
   - Replace `YOUR_BOT_TOKEN_HERE` with your Discord token
   - Customize prefix, settings, etc.

**How to get your Discord token:**
1. Open Discord in browser
2. Press `F12` (Developer Tools)
3. Go to `Network` tab
4. Reload page
5. Find any `discord.com` request
6. Check `Headers` → `Authorization`
7. Copy the token value

### Step 3: Run

```bash
python main.py
```

## 📝 First Commands to Try

1. Check if it works:
   ```
   *help
   ```

2. Test ping:
   ```
   *ping
   ```

3. Try TTS (requires Selenium):
   ```
   *tts Hello world
   ```

4. Take a screenshot:
   ```
   *screenshot https://google.com
   ```

## ⚠️ Important Notes

- **Selenium requires Chrome/Chromium** - Make sure it's installed
- **First run may be slow** - ChromeDriver downloads automatically
- **Headless mode** - Set `"headless": true` in config for background operation
- **Rate limits** - Be careful with spam commands to avoid Discord limits

## 🛠️ Troubleshooting

### ChromeDriver Errors
- Ensure Chrome is installed and up-to-date
- The bot auto-downloads drivers, but you can manually install if needed

### Selenium Timeouts
- Increase `page_load_timeout` in config
- Some websites may block automation

### Token Issues
- Verify token is correct
- Check if account is enabled
- Token format: `xxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxx`

## 📚 Next Steps

- Read the full [README.md](README.md) for all commands
- Check [config/config.json.example](config/config.json.example) for configuration options
- Explore advanced features like web scraping and automation

---

**Remember: Using selfbots violates Discord ToS. Use at your own risk!**
