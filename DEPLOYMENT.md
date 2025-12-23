# Deployment Guide

This guide covers deploying the Discord SelfBot to cloud platforms like DigitalOcean, Heroku, Railway, etc.

## 🔧 Environment Variables (Recommended for Deployment)

Instead of using `config/config.json`, you can use environment variables which is more secure and deployment-friendly.

### Required Environment Variables

- **`DISCORD_TOKEN`** - Your Discord bot token (required)

### Optional Environment Variables

- **`DISCORD_PREFIX`** - Command prefix (default: `*`)
- **`DISCORD_REMOTE_USERS`** - Comma-separated list of user IDs allowed to use commands remotely
- **`DISCORD_AUTOREPLY_MESSAGES`** - Pipe-separated (`|`) list of auto-reply messages
- **`DISCORD_AUTOREPLY_CHANNELS`** - Comma-separated list of channel IDs for auto-reply
- **`DISCORD_AUTOREPLY_USERS`** - Comma-separated list of user IDs for auto-reply
- **`DISCORD_AFK_ENABLED`** - Enable AFK mode (`true` or `false`)
- **`DISCORD_AFK_MESSAGE`** - AFK message
- **`DISCORD_COPYCAT_USERS`** - Comma-separated list of user IDs to copycat
- **`DISCORD_SELENIUM_HEADLESS`** - Run Selenium in headless mode (`true` or `false`, default: `true`)
- **`DISCORD_SELENIUM_IMPLICIT_WAIT`** - Selenium implicit wait in seconds (default: `10`)
- **`DISCORD_SELENIUM_PAGE_LOAD_TIMEOUT`** - Page load timeout in seconds (default: `30`)
- **`DISCORD_SELENIUM_WIDTH`** - Browser window width (default: `1920`)
- **`DISCORD_SELENIUM_HEIGHT`** - Browser window height (default: `1080`)
- **`DISCORD_TTS_PROVIDER`** - TTS provider (default: `elevenlabs`)
- **`DISCORD_TTS_VOICE`** - TTS voice (default: `default`)
- **`DISCORD_TTS_SAVE_PATH`** - TTS save path (default: `temp/tts`)

## 📦 DigitalOcean App Platform

### Step 1: Create App Specification

Create a `app.yaml` file:

```yaml
name: discord-selfbot
services:
- name: discord-selfbot
  github:
    repo: YOUR_USERNAME/discord-selfbot
    branch: master
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DISCORD_TOKEN
    value: YOUR_DISCORD_TOKEN_HERE
    scope: RUN_TIME
    type: SECRET
  - key: DISCORD_PREFIX
    value: "*"
    scope: RUN_TIME
  - key: DISCORD_SELENIUM_HEADLESS
    value: "true"
    scope: RUN_TIME
```

### Step 2: Deploy via DigitalOcean Dashboard

1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Connect your GitHub repository
4. Add environment variables:
   - `DISCORD_TOKEN` (set as SECRET)
   - `DISCORD_PREFIX` (optional)
   - `DISCORD_SELENIUM_HEADLESS=true` (recommended for servers)
5. Set build command: `pip install -r requirements.txt`
6. Set run command: `python main.py`
7. Deploy!

### Step 3: Set Environment Variables in Dashboard

1. Go to your app settings
2. Navigate to "App-Level Environment Variables"
3. Add:
   - `DISCORD_TOKEN` (mark as SECRET)
   - Any other optional variables you need

## 🚂 Railway

### Step 1: Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy!

## 🚀 Heroku

### Step 1: Create `Procfile`

```
worker: python main.py
```

### Step 2: Deploy

```bash
heroku create your-app-name
heroku config:set DISCORD_TOKEN=your_token_here
heroku config:set DISCORD_SELENIUM_HEADLESS=true
git push heroku master
```

## 🐳 Docker Deployment

### Step 1: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p config temp

# Run the bot
CMD ["python", "main.py"]
```

### Step 2: Build and Run

```bash
docker build -t discord-selfbot .
docker run -e DISCORD_TOKEN=your_token_here discord-selfbot
```

## 🔍 Troubleshooting

### "Please set your token in config/config.json"

This error means the bot can't find your token. Solutions:

1. **Use Environment Variables** (Recommended):
   ```bash
   export DISCORD_TOKEN="your_token_here"
   python main.py
   ```

2. **Check File Path**:
   - Ensure `config/config.json` exists
   - Check that the file is in the correct location relative to `main.py`
   - Verify file permissions

3. **Check Working Directory**:
   - The bot should be run from the project root directory
   - Check logs for "Current working directory" and "Script directory"

### Selenium Issues in Deployment

1. **Install Chrome/Chromium**:
   - Most cloud platforms need Chrome installed
   - Use headless mode: `DISCORD_SELENIUM_HEADLESS=true`

2. **System Dependencies**:
   - Some platforms require additional system packages
   - Check platform-specific documentation

### Path Issues

The bot tries multiple paths to find the config:
1. Environment variables (highest priority)
2. `config/config.json` relative to script location
3. `config/config.json` relative to current working directory
4. Creates from `config/config.json.example` if available

Check the logs to see which path was used.

## 📝 Example Environment Variable Setup

```bash
# Required
export DISCORD_TOKEN="your_discord_token_here"

# Optional but recommended
export DISCORD_PREFIX="*"
export DISCORD_SELENIUM_HEADLESS="true"
export DISCORD_SELENIUM_IMPLICIT_WAIT="10"
export DISCORD_SELENIUM_PAGE_LOAD_TIMEOUT="30"

# Optional features
export DISCORD_REMOTE_USERS="123456789,987654321"
export DISCORD_AUTOREPLY_MESSAGES="Hello!|Hi there!|Thanks for the message!"
export DISCORD_AFK_ENABLED="false"
```

## 🔒 Security Best Practices

1. **Never commit `config/config.json`** - It's in `.gitignore`
2. **Use environment variables** for deployment
3. **Mark tokens as SECRET** in your deployment platform
4. **Rotate tokens** if exposed
5. **Use private repositories** if possible

## 📚 Additional Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Railway Docs](https://docs.railway.app/)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)

