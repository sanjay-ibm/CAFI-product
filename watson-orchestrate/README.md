# Watson Orchestrate Integration for Product Search

This directory contains the Watson Orchestrate skill definition and deployment tools for the IBM Product Catalog API.

## 📋 Overview

The Watson Orchestrate skill enables users to search for IBM products using natural language queries through Watson Orchestrate's conversational interface. The skill integrates with the Product Catalog API to provide:

- **Product Search**: Find IBM products by name, code, or description
- **Product Details**: Retrieve detailed information about specific products
- **Fuzzy Matching**: Advanced search with typo tolerance and similarity scoring

## 🗂️ Files

```
watson-orchestrate/
├── product-search-skill.yaml      # OpenAPI 3.0 specification for Watson Orchestrate
├── orchestrate-config.json        # Deployment configuration
├── deploy-to-orchestrate.py       # Python deployment script
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Watson Orchestrate Account**
   - Access to IBM Watson Orchestrate
   - API credentials (API key)
   - Tenant ID (if applicable)

2. **Product Catalog API**
   - API must be deployed and accessible
   - URL: `https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com`

3. **Python Environment**
   ```bash
   pip install requests pyyaml python-dotenv
   ```

### Step 1: Configure Environment Variables

Update the `.env` file in the project root:

```bash
# Watson Orchestrate API Credentials
ORCHESTRATE_API_KEY=your_api_key_here
ORCHESTRATE_API_URL=https://api.orchestrate.ibm.com
ORCHESTRATE_TENANT_ID=your_tenant_id_here  # Optional
ORCHESTRATE_REGION=us-south                # Optional
```

### Step 2: Deploy the Skill

```bash
# Deploy new skill
python watson-orchestrate/deploy-to-orchestrate.py

# Update existing skill
python watson-orchestrate/deploy-to-orchestrate.py --update

# Custom paths
python watson-orchestrate/deploy-to-orchestrate.py \
  --spec watson-orchestrate/product-search-skill.yaml \
  --config watson-orchestrate/orchestrate-config.json
```

### Step 3: Verify Deployment

1. Log in to Watson Orchestrate: https://api.orchestrate.ibm.com
2. Navigate to **Skills** section
3. Find **IBM Product Search** skill
4. Test with sample queries:
   - "Find IBM Cloud Pak for Data"
   - "Search for product 5737-H33"
   - "What is WebSphere?"

## 🎯 Skill Capabilities

### 1. Search IBM Products

**Natural Language Examples:**
- "Find products related to Cloud Pak"
- "Search for IBM WebSphere"
- "What products match DB2?"
- "Show me products with code 5737"

**Parameters:**
- `query` (required): Search term or product code
- `limit` (optional): Max results (default: 10)
- `threshold` (optional): Match confidence (default: 0.70)

**Response:**
```json
{
  "query": "Cloud Pak",
  "results": [
    {
      "score": 1.0,
      "product_code": "5737-H33",
      "product_name": "IBM Cloud Pak for Data",
      "matched_aliases": ["cloud pak for data", "cp4d"]
    }
  ],
  "result_count": 1,
  "execution_time_ms": 12.5
}
```

### 2. Get Product Details

**Natural Language Examples:**
- "Get details for product 5737-H33"
- "What is product code 5724-A12?"
- "Show me information about 5655-Y04"

**Parameters:**
- `product_code` (required): IBM product code (SLC_CODE)

**Response:**
```json
{
  "product_code": "5737-H33",
  "product_name": "IBM Cloud Pak for Data"
}
```

## 🔧 Configuration

### OpenAPI Specification (`product-search-skill.yaml`)

The OpenAPI spec defines:
- API endpoints and operations
- Request/response schemas
- Watson Orchestrate skill metadata
- Authentication requirements

**Key Sections:**
```yaml
x-ibm-skill:
  name: "Search IBM Products"
  description: "Find IBM product information"
  input:
    - name: query
      description: "Product name or code"
      required: true
  output:
    description: "List of matching products"
```

### Deployment Configuration (`orchestrate-config.json`)

Customize deployment settings:

```json
{
  "skill": {
    "name": "IBM Product Search",
    "description": "Search IBM product catalog",
    "version": "1.0.0",
    "category": "Information Retrieval",
    "tags": ["IBM", "products", "search"]
  },
  "api": {
    "base_url": "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com",
    "authentication": {
      "type": "none"
    }
  }
}
```

## 🛠️ Advanced Usage

### Custom Deployment Script

```python
from watson_orchestrate import OrchestrateDeployer

deployer = OrchestrateDeployer()

# Load and deploy
openapi_spec = deployer.load_openapi_spec('product-search-skill.yaml')
config = deployer.load_config('orchestrate-config.json')

skill_id = deployer.create_skill(openapi_spec, config)
print(f"Deployed skill: {skill_id}")
```

### Update Existing Skill

```bash
# Find existing skill ID
python watson-orchestrate/deploy-to-orchestrate.py --list

# Update specific skill
python watson-orchestrate/deploy-to-orchestrate.py --update --skill-id abc123
```

### Testing the Skill

```bash
# Test API endpoint directly
curl "https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/products/search?query=Cloud+Pak"

# Test through Watson Orchestrate
# Use the Watson Orchestrate UI or API to invoke the skill
```

## 📊 Monitoring and Troubleshooting

### Check Skill Status

```python
deployer = OrchestrateDeployer()
skills = deployer.list_skills()

for skill in skills:
    print(f"{skill['name']}: {skill['status']}")
```

### Common Issues

#### 1. Authentication Failed
```
❌ Failed to connect to Watson Orchestrate API: 401 Unauthorized
```

**Solution:**
- Verify `ORCHESTRATE_API_KEY` in `.env`
- Check API key is valid and not expired
- Ensure correct API URL

#### 2. Skill Already Exists
```
⚠️ Skill 'IBM Product Search' already exists
```

**Solution:**
```bash
# Update existing skill
python watson-orchestrate/deploy-to-orchestrate.py --update
```

#### 3. API Connection Failed
```
❌ Failed to connect to Watson Orchestrate API: Connection timeout
```

**Solution:**
- Check network connectivity
- Verify `ORCHESTRATE_API_URL` is correct
- Check firewall/proxy settings

#### 4. Invalid OpenAPI Spec
```
❌ Failed to create skill: Invalid OpenAPI specification
```

**Solution:**
- Validate OpenAPI spec: https://editor.swagger.io/
- Check required fields are present
- Ensure proper YAML formatting

### Health Check

```bash
# Check Product Catalog API health
curl https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/health

# Expected response:
{
  "status": "healthy",
  "matcher_type": "enhanced",
  "total_products": 5000,
  "total_aliases": 10000
}
```

## 🔐 Security

### API Key Management

**Best Practices:**
- Store API keys in `.env` file (never commit to git)
- Use environment-specific keys (dev, staging, prod)
- Rotate keys regularly
- Use IBM Cloud Secrets Manager for production

### Authentication Options

The skill currently uses **no authentication** for the Product Catalog API. To add authentication:

1. **Update OpenAPI Spec:**
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

2. **Update Configuration:**
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

## 📚 Additional Resources

### Watson Orchestrate Documentation
- [Watson Orchestrate Overview](https://www.ibm.com/cloud/watson-orchestrate)
- [Skill Development Guide](https://cloud.ibm.com/docs/watson-orchestrate)
- [OpenAPI Integration](https://cloud.ibm.com/docs/watson-orchestrate?topic=watson-orchestrate-openapi)

### Product Catalog API
- [API Documentation](https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com/docs)
- [GitHub Repository](../README.md)
- [Deployment Guide](../docs/deployment/OPENSHIFT_DEPLOYMENT.md)

### OpenAPI Specification
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)

## 🤝 Support

For issues or questions:

1. **Product Catalog API Issues**
   - Check [Troubleshooting Guide](../docs/troubleshooting/TROUBLESHOOTING.md)
   - Review API logs in OpenShift
   - Contact: cafi-support@ibm.com

2. **Watson Orchestrate Issues**
   - Check Watson Orchestrate documentation
   - Review skill deployment logs
   - Contact IBM Watson support

3. **Integration Issues**
   - Verify API connectivity
   - Check OpenAPI spec validation
   - Review deployment script logs

## 📝 Version History

- **v1.0.0** (2026-04-21)
  - Initial release
  - Product search skill
  - Product details retrieval
  - OpenAPI 3.0 specification
  - Python deployment script

## 🔄 Future Enhancements

- [ ] Add authentication support
- [ ] Implement skill versioning
- [ ] Add batch product search
- [ ] Support for product recommendations
- [ ] Integration with Watson Assistant
- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Export search results

---

**Made with Bob** 🤖