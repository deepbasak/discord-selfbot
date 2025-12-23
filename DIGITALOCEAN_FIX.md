# DigitalOcean Deployment Fix

## Problem
The bot was showing: `❌ Please set your token in config/config.json` even though the token was set correctly.

## Root Cause
The bot was using relative paths to find the config file, which can fail in deployment environments where the working directory differs.

## Solution
The bot now supports **environment variables** (recommended for deployments) and has improved path resolution.

## Quick Fix for DigitalOcean

### Option 1: Use Environment Variables (Recommended)

1. Go to your DigitalOcean App Platform dashboard
2. Navigate to your app → Settings → App-Level Environment Variables
3. Add these variables:

   **Required:**
   - `DISCORD_TOKEN` = `your_discord_token_here` (mark as **SECRET**)

   **Optional (but recommended):**
   - `DISCORD_PREFIX` = `*`
   - `DISCORD_SELENIUM_HEADLESS` = `true`

4. Save and redeploy

### Option 2: Ensure Config File is in Correct Location

If you prefer using `config/config.json`:

1. Make sure the file exists at the project root: `config/config.json`
2. Verify the file has correct permissions
3. Check that the file is not empty and contains valid JSON
4. The bot will now try multiple paths to find it

## Verification

After deploying, check the logs. You should see:
- `[INFO] Loaded configuration from environment variables` (if using env vars)
- `[INFO] Loaded configuration from: /path/to/config.json` (if using file)

If you still see the error, the logs will now show:
- Current working directory
- Script directory
- All paths that were tried

This will help diagnose the issue.

## Testing Locally

You can test the environment variable approach locally:

```bash
# Windows PowerShell
$env:DISCORD_TOKEN="your_token_here"
python main.py

# Windows CMD
set DISCORD_TOKEN=your_token_here
python main.py

# Linux/macOS
export DISCORD_TOKEN="your_token_here"
python main.py
```

## What Changed

1. **Environment Variable Support**: The bot now reads `DISCORD_TOKEN` from environment variables
2. **Better Path Resolution**: Tries multiple paths to find config.json
3. **Improved Error Messages**: Shows exactly what paths were checked
4. **Fallback to Example**: Creates config from example if not found

## Next Steps

1. Update your DigitalOcean deployment with the `DISCORD_TOKEN` environment variable
2. Redeploy your app
3. Check the logs to confirm it's working

If you still have issues, check the deployment logs for the detailed path information.

