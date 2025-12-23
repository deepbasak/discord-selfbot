# Quick Fix for DigitalOcean Deployment

## Issues Fixed

1. ✅ **Token not found** - Added environment variable support and better path resolution
2. ✅ **Health check failures** - Added HTTP health check endpoint on port 8080

## Immediate Steps to Fix Your Deployment

### Step 1: Set Environment Variable in DigitalOcean

1. Go to your DigitalOcean App Platform dashboard
2. Navigate to: **Your App → Settings → App-Level Environment Variables**
3. Click **"Edit"** or **"Add Variable"**
4. Add:
   - **Key**: `DISCORD_TOKEN`
   - **Value**: `your_discord_token_here` (paste your actual token)
   - **Type**: Select **"SECRET"** (important!)
   - **Scope**: Select **"RUN_TIME"**
5. Click **"Save"**

### Step 2: Optional Environment Variables

You can also add these (optional but recommended):

- `DISCORD_PREFIX` = `*`
- `DISCORD_SELENIUM_HEADLESS` = `true`
- `HEALTH_CHECK_PORT` = `8080`

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click **"Create Deployment"** or **"Redeploy"**
3. Wait for deployment to complete

## What Changed in the Code

### 1. Environment Variable Support
The bot now automatically reads `DISCORD_TOKEN` from environment variables, which is the standard way to handle secrets in cloud deployments.

### 2. Health Check Endpoint
Added an HTTP server on port 8080 that responds to `/health` requests. This satisfies DigitalOcean's health check requirements.

### 3. Better Debugging
The bot now prints detailed information about:
- Whether config was loaded
- Where config was loaded from
- Token presence and length (without exposing the actual token)

## Verification

After redeploying, check the logs. You should see:

```
[INFO] Loaded configuration from environment variables
[INFO] Health check server started on port 8080
[DEBUG] Config loaded: True
[DEBUG] Token present: True
[DEBUG] Token length: 59
✅ Bot logged in as YourUsername#1234
```

## If It Still Doesn't Work

1. **Check the logs** - Look for the `[DEBUG]` messages to see what's happening
2. **Verify environment variable** - Make sure `DISCORD_TOKEN` is set as a SECRET type
3. **Check token format** - Discord tokens are usually 59 characters long
4. **Verify health check** - The health check should respond on `/health` endpoint

## Alternative: Using Config File

If you prefer using `config/config.json` instead of environment variables:

1. Make sure the file exists in your repository (but don't commit the actual token!)
2. Use DigitalOcean's build-time secrets or file mounting
3. The bot will try multiple paths to find the config file

**However, using environment variables is strongly recommended for security.**

## Troubleshooting

### "Token not found" error persists

Check the logs for:
- `[DEBUG] Config loaded: False` - Config not loading at all
- `[DEBUG] Token present: False` - Token not in config
- `[DEBUG] Token length: 0` - Token is empty

### Health check still failing

- Verify port 8080 is accessible
- Check that the health check path is `/health`
- Look for `[INFO] Health check server started on port 8080` in logs

### Bot exits immediately

- Check for any error messages in the logs
- Verify the token is valid (not expired, correct format)
- Make sure all dependencies are installed

