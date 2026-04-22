# Quick Ngrok Setup - Complete Guide

## Current Status
✅ ngrok.exe is installed at: C:\ngrok\ngrok.exe
✅ ngrok version: 3.37.3
✅ PATH has been updated

## Important: Refresh Your PowerShell Session

The PATH was updated, but your current PowerShell session doesn't see it yet. You have 2 options:

### Option 1: Refresh Current Session (Quick)
Run this command in your current PowerShell:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Then test:
```powershell
ngrok version
```

### Option 2: Restart PowerShell (Recommended)
1. Close this PowerShell window
2. Open a NEW PowerShell window
3. Test: `ngrok version`

## Complete Setup Steps

### Step 1: Configure Ngrok (One-time)
Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 2: Start Your API
In Terminal 1:
```powershell
cd c:/Users/SANJAYSRIVASTAVA/CAFI-product
python app.py
```

Your API will start on http://localhost:5000

### Step 3: Start Ngrok
In Terminal 2 (new PowerShell window):
```powershell
cd c:/Users/SANJAYSRIVASTAVA/CAFI-product
ngrok http 5000
```

You'll see output like:
```
Forwarding    https://abc123def456.ngrok-free.app -> http://localhost:5000
```

### Step 4: Update OpenAPI Spec
Copy your ngrok URL (e.g., `abc123def456.ngrok-free.app`)

Edit `product-catalog-api-openapi.yaml`:
```yaml
servers:
  - url: https://abc123def456.ngrok-free.app
    description: Ngrok tunnel
```

### Step 5: Test Your Public API
```powershell
# Test health
curl https://abc123def456.ngrok-free.app/health

# Test products
curl https://abc123def456.ngrok-free.app/products

# Test search
curl "https://abc123def456.ngrok-free.app/products/search?query=5737-H33"
```

## Using the Provided Scripts

### Refresh PATH in Current Session:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Start Ngrok with Script:
```powershell
.\start-ngrok.ps1
```

## Quick Reference

### Check if ngrok is working:
```powershell
ngrok version
```

### Start ngrok on different port:
```powershell
ngrok http 8000
```

### View ngrok dashboard:
Open browser: http://localhost:4040

### Stop ngrok:
Press `Ctrl+C` in the ngrok terminal

## Troubleshooting

### "ngrok: command not found"
Run this to refresh PATH:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Or restart PowerShell.

### "ERR_NGROK_108"
Configure your authtoken:
```powershell
ngrok config add-authtoken YOUR_TOKEN
```

### "tunnel not found"
Make sure your API is running first:
```powershell
python app.py
```

## Summary

Your setup is complete! Just remember:
1. **Refresh PATH** in current session OR restart PowerShell
2. **Configure authtoken** (one-time)
3. **Start API** first
4. **Start ngrok** second
5. **Update OpenAPI spec** with ngrok URL
6. **Test** your public API

Your local API data is now accessible via ngrok URL! 🎉