# Complete Guide: Host Your Local API on Ngrok

This guide will walk you through hosting your Product Catalog API from localhost to a public ngrok URL.

## Step-by-Step Process

### Step 1: Install Ngrok

#### For Windows:
1. Go to https://ngrok.com/download
2. Download the Windows version (ZIP file)
3. Extract to a folder (e.g., `C:\ngrok`)
4. Add to PATH or use full path

#### Quick Install (PowerShell as Administrator):
```powershell
# Download ngrok
Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"

# Extract
Expand-Archive -Path "ngrok.zip" -DestinationPath "C:\ngrok"

# Add to PATH (optional)
$env:Path += ";C:\ngrok"
```

### Step 2: Sign Up and Get Auth Token

1. Go to https://dashboard.ngrok.com/signup
2. Sign up for a free account
3. Go to https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken

### Step 3: Configure Ngrok

```powershell
# Configure your authtoken (one-time setup)
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

Replace `YOUR_AUTH_TOKEN_HERE` with your actual token from the dashboard.

### Step 4: Start Your Local API

Open a **NEW PowerShell terminal** and run:

```powershell
# Navigate to your project directory
cd c:/Users/SANJAYSRIVASTAVA/CAFI-product

# Start your Flask API
python app.py
```

**OR** if your main file is in src/api:
```powershell
python src/api/app.py
```

You should see output like:
```
* Running on http://127.0.0.1:5000
* Running on http://localhost:5000
```

**Note the port number** (usually 5000 for Flask).

### Step 5: Start Ngrok Tunnel

Open **ANOTHER PowerShell terminal** (keep your API running in the first one):

```powershell
# Navigate to project directory
cd c:/Users/SANJAYSRIVASTAVA/CAFI-product

# Start ngrok on the same port as your API
ngrok http 5000
```

You'll see output like this:
```
ngrok

Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123def456.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copy the Forwarding URL**: `https://abc123def456.ngrok-free.app`

### Step 6: Update Your OpenAPI Specification

1. Open `product-catalog-api-openapi.yaml`
2. Find the line with `YOUR_NGROK_URL`
3. Replace it with your actual ngrok subdomain

**Before:**
```yaml
servers:
  - url: https://YOUR_NGROK_URL.ngrok-free.app
```

**After:**
```yaml
servers:
  - url: https://abc123def456.ngrok-free.app
```

### Step 7: Test Your Public API

Open a **NEW PowerShell terminal** or use your browser:

```powershell
# Test health endpoint
curl https://abc123def456.ngrok-free.app/health

# Test products endpoint
curl https://abc123def456.ngrok-free.app/products

# Test search endpoint
curl "https://abc123def456.ngrok-free.app/products/search?query=5737-H33"
```

**Or use your browser:**
- https://abc123def456.ngrok-free.app/products
- https://abc123def456.ngrok-free.app/health

### Step 8: Monitor Traffic (Optional)

Open your browser and go to: http://localhost:4040

This shows:
- All incoming requests
- Request/response details
- Ability to replay requests
- Traffic statistics

## Complete Example Session

Here's what your complete workflow looks like:

### Terminal 1 - Start API:
```powershell
PS C:\Users\SANJAYSRIVASTAVA\CAFI-product> python app.py
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### Terminal 2 - Start Ngrok:
```powershell
PS C:\Users\SANJAYSRIVASTAVA\CAFI-product> ngrok http 5000

Forwarding    https://abc123def456.ngrok-free.app -> http://localhost:5000
```

### Terminal 3 - Test API:
```powershell
PS C:\Users\SANJAYSRIVASTAVA\CAFI-product> curl https://abc123def456.ngrok-free.app/products
{
  "products": [...],
  "count": 100
}
```

## Using the PowerShell Script

Alternatively, use the provided script:

```powershell
# Make sure your API is running first in another terminal
python app.py

# Then in a new terminal, run:
.\start-ngrok.ps1

# Or specify a different port:
.\start-ngrok.ps1 8000
```

## Important Notes

### Your Data is Already There!
Your local API already has access to:
- `data/product_match_dictionary.json` - Your product data
- `data/Product_Match_Dictionary_Watson.xlsx` - Excel data

When you start ngrok, it creates a tunnel to your **running local API**, which already has access to all your local data files. No need to upload or move data!

### How It Works:
```
Internet Request → Ngrok Cloud → Ngrok Tunnel → Your Local API → Your Local Data Files
```

### Free Tier Limitations:
- **Random URL**: Each time you restart ngrok, you get a new URL
- **Session Time**: Free sessions expire after 2 hours
- **Ngrok Banner**: Free tier shows a warning page (click "Visit Site")

### To Get a Permanent URL:
Upgrade to ngrok paid plan for:
- Custom subdomain (e.g., `my-api.ngrok-free.app`)
- No session timeout
- No warning banner

## Troubleshooting

### Problem: "command not found: ngrok"
**Solution**: 
```powershell
# Use full path
C:\ngrok\ngrok.exe http 5000

# Or add to PATH permanently
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ngrok", "User")
```

### Problem: "ERR_NGROK_108"
**Solution**: Configure your authtoken
```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Problem: "tunnel not found" or "connection refused"
**Solution**: Make sure your API is running first
```powershell
# Check if API is running
curl http://localhost:5000/health

# If not, start it
python app.py
```

### Problem: Can't access data files
**Solution**: Ensure your Flask app uses correct relative paths
```python
# In your app.py or src/api/app.py
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'product_match_dictionary.json')
```

## Security Tips

1. **Don't share your ngrok URL publicly** if it contains sensitive data
2. **Add authentication** to your API endpoints
3. **Monitor the ngrok dashboard** at http://localhost:4040
4. **Stop ngrok** when not in use (Ctrl+C)
5. **Use environment variables** for sensitive config

## Quick Reference Commands

```powershell
# Start API
python app.py

# Start ngrok
ngrok http 5000

# Test locally
curl http://localhost:5000/products

# Test via ngrok
curl https://YOUR-NGROK-URL.ngrok-free.app/products

# View ngrok dashboard
# Open browser: http://localhost:4040

# Stop ngrok
# Press Ctrl+C in the ngrok terminal

# Stop API
# Press Ctrl+C in the API terminal
```

## Next Steps

After your API is accessible via ngrok:

1. **Share the URL** with team members or clients
2. **Test from different devices** (phone, tablet, etc.)
3. **Integrate with other services** that need a public URL
4. **Use for webhook testing** if needed
5. **Monitor usage** via ngrok dashboard

## Need Help?

- Ngrok Documentation: https://ngrok.com/docs
- Ngrok Dashboard: https://dashboard.ngrok.com
- Project Documentation: See `docs/deployment/NGROK_SETUP.md`