# Watson Orchestrate Quick Start Guide

Get your Product Search skill deployed to Watson Orchestrate in 5 minutes!

## ⚡ Quick Deploy (5 Minutes)

### 1. Prerequisites (1 min)

```bash
# Check Python version (need 3.8+)
python --version

# Install dependencies
pip install requests pyyaml python-dotenv
```

### 2. Configure API Key (1 min)

Edit `.env` file in project root:

```bash
ORCHESTRATE_API_KEY=your_api_key_here
ORCHESTRATE_API_URL=https://api.orchestrate.ibm.com
```

**Get your API key:**
- Login: https://api.orchestrate.ibm.com
- Settings → API Keys → Create API Key

### 3. Deploy (2 min)

```bash
# Deploy the skill
python watson-orchestrate/deploy-to-orchestrate.py

# Expected output:
# ✅ Skill created successfully!
# Skill ID: abc123-def456-ghi789
```

### 4. Test (1 min)

```bash
# Test the API
curl "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/search?query=Cloud%20Pak"
```

### 5. Use in Watson Orchestrate

1. Login: https://api.orchestrate.ibm.com
2. Go to **Skills** → Find **IBM Product Search**
3. Click **Test** → Try: "Find IBM Cloud Pak for Data"

## 🎯 Common Use Cases

### Search for Products

**Natural Language:**
- "Find products related to Cloud Pak"
- "Search for IBM WebSphere"
- "What is product 5737-H33?"

**API Call:**
```bash
curl "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/search?query=Cloud%20Pak&limit=10"
```

### Get Product Details

**Natural Language:**
- "Get details for product 5737-H33"
- "What is product code 5724-A12?"

**API Call:**
```bash
curl "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/5737-H33"
```

## 🔄 Update Existing Skill

```bash
# Update deployed skill
python watson-orchestrate/deploy-to-orchestrate.py --update
```

## 🐛 Quick Troubleshooting

### Authentication Error
```bash
# Check API key
cat .env | grep ORCHESTRATE_API_KEY

# Regenerate key if needed
# Login → Settings → API Keys → Create New
```

### Skill Already Exists
```bash
# Update instead of create
python watson-orchestrate/deploy-to-orchestrate.py --update
```

### API Not Responding
```bash
# Check API health
curl https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/health
```

## 📚 Full Documentation

- [Complete Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Integration README](./README.md)
- [API Documentation](https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/docs)

## 🆘 Need Help?

- **API Issues**: cafi-support@ibm.com
- **Watson Orchestrate**: IBM Watson Support
- **Documentation**: See [README.md](./README.md)

---

**Made with Bob** 🤖