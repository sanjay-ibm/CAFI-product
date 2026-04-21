# Watson Orchestrate Deployment Guide

Complete step-by-step guide to deploy the Product Search skill to Watson Orchestrate.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Watson Orchestrate account with admin access
- [ ] Watson Orchestrate API key
- [ ] Product Catalog API deployed and accessible
- [ ] Python 3.8+ installed
- [ ] Required Python packages: `requests`, `pyyaml`, `python-dotenv`

## 🚀 Deployment Steps

### Step 1: Verify API Accessibility

First, ensure your Product Catalog API is accessible:

```bash
# Test production API
curl https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/health

# Expected response:
{
  "status": "healthy",
  "matcher_type": "enhanced",
  "total_products": 5000,
  "total_aliases": 10000
}
```

### Step 2: Configure Environment Variables

1. Open the `.env` file in the project root
2. Add your Watson Orchestrate credentials:

```bash
# Watson Orchestrate API Credentials
ORCHESTRATE_API_KEY=your_api_key_here
ORCHESTRATE_API_URL=https://api.orchestrate.ibm.com
ORCHESTRATE_TENANT_ID=your_tenant_id_here  # Optional
ORCHESTRATE_REGION=us-south                # Optional
```

**To get your API key:**
1. Log in to Watson Orchestrate: https://api.orchestrate.ibm.com
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the key and paste it in `.env`

### Step 3: Install Python Dependencies

```bash
# Install required packages
pip install requests pyyaml python-dotenv

# Or use requirements file
pip install -r config/requirements.txt
```

### Step 4: Validate OpenAPI Specification

Before deploying, validate the OpenAPI spec:

```bash
# Option 1: Use online validator
# Visit: https://editor.swagger.io/
# Copy contents of watson-orchestrate/product-search-skill.yaml

# Option 2: Use Python validation
python -c "import yaml; yaml.safe_load(open('watson-orchestrate/product-search-skill.yaml'))"
```

### Step 5: Deploy to Watson Orchestrate

#### First-Time Deployment

```bash
# Deploy new skill
python watson-orchestrate/deploy-to-orchestrate.py
```

Expected output:
```
======================================================================
🤖 Watson Orchestrate Skill Deployment
======================================================================
📖 Loading OpenAPI spec from watson-orchestrate/product-search-skill.yaml...
✅ Loaded OpenAPI spec: Product Search Skill for Watson Orchestrate v1.0.0
📖 Loading configuration from watson-orchestrate/orchestrate-config.json...
✅ Loaded configuration for skill: IBM Product Search
🔌 Validating connection to https://api.orchestrate.ibm.com...
✅ Successfully connected to Watson Orchestrate API

📋 Listing existing skills...
✅ Found 0 existing skills

🚀 Creating skill: IBM Product Search...
✅ Skill created successfully!
   Skill ID: abc123-def456-ghi789

======================================================================
✅ Deployment completed successfully!
======================================================================

📝 Next steps:
   1. Log in to Watson Orchestrate: https://api.orchestrate.ibm.com
   2. Navigate to Skills section
   3. Find your skill: IBM Product Search
   4. Test the skill with sample queries
   5. Add the skill to your assistant or workflow
```

#### Update Existing Skill

```bash
# Update existing skill
python watson-orchestrate/deploy-to-orchestrate.py --update
```

### Step 6: Verify Deployment in Watson Orchestrate

1. **Log in to Watson Orchestrate**
   - URL: https://api.orchestrate.ibm.com
   - Use your IBM credentials

2. **Navigate to Skills**
   - Click on **Skills** in the left sidebar
   - Look for **IBM Product Search** skill

3. **Check Skill Status**
   - Status should be **Active** or **Ready**
   - Version should be **1.0.0**

4. **Review Skill Details**
   - Click on the skill name
   - Verify endpoints are configured:
     - `searchProducts`
     - `getProductByCode`

### Step 7: Test the Skill

#### Test in Watson Orchestrate UI

1. **Open Skill Testing Interface**
   - Click on **IBM Product Search** skill
   - Click **Test** button

2. **Test Search Products**
   ```
   Input: "Find IBM Cloud Pak for Data"
   Expected: List of matching products with scores
   ```

3. **Test Get Product Details**
   ```
   Input: "Get details for product 5737-H33"
   Expected: Product code and name
   ```

#### Test via API

```bash
# Test search endpoint
curl -X GET "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/search?query=Cloud%20Pak&limit=5" \
  -H "Accept: application/json"

# Test product details endpoint
curl -X GET "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/5737-H33" \
  -H "Accept: application/json"
```

### Step 8: Create Watson Assistant Integration (Optional)

1. **Create New Assistant**
   - Navigate to **Assistants** section
   - Click **Create Assistant**
   - Name: "Product Search Assistant"

2. **Add Skill to Assistant**
   - Open the assistant
   - Click **Add Skill**
   - Select **IBM Product Search**
   - Click **Add**

3. **Configure Intents**
   - Create intent: `#search_product`
   - Add training phrases:
     - "Find products"
     - "Search for IBM products"
     - "What products do you have?"

4. **Create Dialog Flow**
   ```
   User: "Find Cloud Pak products"
   Assistant: Calls searchProducts skill
   Assistant: Displays results
   ```

### Step 9: Monitor and Maintain

#### Check Skill Health

```bash
# Run health check
python watson-orchestrate/deploy-to-orchestrate.py --health-check
```

#### View Skill Logs

1. Log in to Watson Orchestrate
2. Navigate to **Skills** → **IBM Product Search**
3. Click **Logs** tab
4. Review recent invocations and errors

#### Update Skill Configuration

To update the skill configuration:

1. Edit `watson-orchestrate/orchestrate-config.json`
2. Run update command:
   ```bash
   python watson-orchestrate/deploy-to-orchestrate.py --update
   ```

## 🔧 Advanced Configuration

### Custom API Base URL

To use a different API endpoint:

1. Edit `watson-orchestrate/orchestrate-config.json`:
   ```json
   {
     "api": {
       "base_url": "https://your-custom-api.example.com"
     }
   }
   ```

2. Redeploy:
   ```bash
   python watson-orchestrate/deploy-to-orchestrate.py --update
   ```

### Add Authentication

To add API key authentication:

1. Update OpenAPI spec (`product-search-skill.yaml`):
   ```yaml
   components:
     securitySchemes:
       ApiKeyAuth:
         type: apiKey
         in: header
         name: X-API-Key
   
   security:
     - ApiKeyAuth: []
   ```

2. Update configuration:
   ```json
   {
     "api": {
       "authentication": {
         "type": "apiKey",
         "header": "X-API-Key",
         "value": "${API_KEY}"
       }
     }
   }
   ```

3. Redeploy the skill

### Custom Skill Parameters

To customize default parameters:

Edit `watson-orchestrate/orchestrate-config.json`:
```json
{
  "skills": [
    {
      "id": "search_products",
      "input_parameters": [
        {
          "name": "limit",
          "default": 20  // Changed from 10
        },
        {
          "name": "threshold",
          "default": 0.80  // Changed from 0.70
        }
      ]
    }
  ]
}
```

## 🐛 Troubleshooting

### Issue: Authentication Failed

**Error:**
```
❌ Failed to connect to Watson Orchestrate API: 401 Unauthorized
```

**Solutions:**
1. Verify API key in `.env` file
2. Check API key hasn't expired
3. Ensure correct API URL
4. Try regenerating API key

### Issue: Skill Already Exists

**Error:**
```
⚠️ Skill 'IBM Product Search' already exists
```

**Solutions:**
```bash
# Option 1: Update existing skill
python watson-orchestrate/deploy-to-orchestrate.py --update

# Option 2: Delete and recreate
# (Delete via Watson Orchestrate UI first)
python watson-orchestrate/deploy-to-orchestrate.py
```

### Issue: API Connection Timeout

**Error:**
```
❌ Failed to connect to Watson Orchestrate API: Connection timeout
```

**Solutions:**
1. Check network connectivity
2. Verify firewall settings
3. Check proxy configuration
4. Try different network

### Issue: Invalid OpenAPI Spec

**Error:**
```
❌ Failed to create skill: Invalid OpenAPI specification
```

**Solutions:**
1. Validate spec at https://editor.swagger.io/
2. Check YAML syntax
3. Verify all required fields
4. Review error message details

### Issue: Skill Not Responding

**Symptoms:**
- Skill shows as "Active" but doesn't respond
- Timeout errors when invoking skill

**Solutions:**
1. Check Product Catalog API health:
   ```bash
   curl https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/health
   ```

2. Verify API is accessible from Watson Orchestrate
3. Check API logs in OpenShift
4. Review skill configuration

## 📊 Monitoring and Analytics

### View Skill Usage

1. Log in to Watson Orchestrate
2. Navigate to **Analytics** → **Skills**
3. Select **IBM Product Search**
4. View metrics:
   - Total invocations
   - Success rate
   - Average response time
   - Error rate

### Set Up Alerts

1. Navigate to **Settings** → **Alerts**
2. Create alert for skill errors
3. Configure notification channels
4. Set threshold (e.g., >5% error rate)

## 🔐 Security Best Practices

1. **API Key Management**
   - Store keys in `.env` (never commit)
   - Rotate keys every 90 days
   - Use separate keys for dev/prod
   - Monitor key usage

2. **Access Control**
   - Limit skill access to authorized users
   - Use role-based access control
   - Review access logs regularly

3. **Data Privacy**
   - Don't log sensitive data
   - Implement data retention policies
   - Comply with GDPR/privacy regulations

## 📚 Additional Resources

- [Watson Orchestrate Documentation](https://cloud.ibm.com/docs/watson-orchestrate)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Product Catalog API Docs](https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/docs)
- [Integration README](./README.md)

## 🆘 Support

For assistance:
- **Product Catalog API**: cafi-support@ibm.com
- **Watson Orchestrate**: IBM Watson Support
- **Documentation**: See [README.md](./README.md)

---

**Last Updated**: 2026-04-21  
**Version**: 1.0.0  
**Made with Bob** 🤖