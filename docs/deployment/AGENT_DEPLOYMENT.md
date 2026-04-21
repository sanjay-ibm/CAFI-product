# IBM Orchestrate Agent Deployment Guide

This guide explains how to deploy the IBM Product Catalog Agent to IBM Orchestrate.

## Overview

The agent consists of:
- **Agent Definition**: `ibm-orchestrate-agent.yaml` - Main agent configuration
- **OpenAPI Specification**: `product-catalog-api-openapi.yaml` - Defines all API tools

## Prerequisites

- IBM Orchestrate CLI installed and configured
- Access to IBM Orchestrate environment
- Product Catalog API deployed and accessible

## Deployment Steps

### Step 1: Import Tools from OpenAPI Specification

Import all tools at once using the OpenAPI specification file:

```powershell
# Import all tools from OpenAPI spec
orchestrate tools import --file ibm-orchestrate-tool-search-products.yaml
Usage: orchestrate tools import [OPTIONS]
Try 'orchestrate tools import --help' for help.
╭─ Error ───────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing option '--kind' / '-k'. Choose from:                                                      │
│         openapi,                                                                                  │
│         python,                                                                                   │
│         flow,                                                                                     │
│         langflow                                  
```

This will create three tools:
- `get_products` - List all products
- `search_products` - Search products by query
- `get_product` - Get specific product by code

### Step 2: Verify Tools

Verify that all tools were imported successfully:

```powershell
orchestrate tools list
```

You should see:
- `get_products`
- `search_products`
- `get_product`

### Step 3: Import Agent

Once all tools are imported, import the agent:

```powershell
orchestrate agents import --file ibm-orchestrate-agent.yaml
```

### Step 4: Verify Agent

Verify the agent was imported successfully:

```powershell
orchestrate agents list
```

You should see `ibm_product_catalog_agent` in the list.

## File Structure

```
CAFI-product/
├── ibm-orchestrate-agent.yaml          # Main agent configuration
├── product-catalog-api-openapi.yaml    # OpenAPI spec with all tools
├── ibm-orchestrate-tool-*.yaml         # (Legacy - not used)
```

**Note**: The individual tool YAML files (`ibm-orchestrate-tool-*.yaml`) are not used. All tools are defined in the OpenAPI specification file.

## Tool Definitions

### get_products
- **Endpoint**: `GET /products`
- **Purpose**: List all available IBM products
- **Parameters**: None

### search_products
- **Endpoint**: `GET /products/search`
- **Purpose**: Search products by query string
- **Parameters**: 
  - `query` (required): Search term for finding products

### get_product
- **Endpoint**: `GET /products/{SLC_CODE}`
- **Purpose**: Get specific product by SLC code
- **Parameters**:
  - `SLC_CODE` (required): IBM product SLC code (e.g., 5737-H33)

## Agent Configuration

The agent is configured with:
- **LLM**: `groq/openai/gpt-oss-120b`
- **Temperature**: 0.7
- **Style**: default
- **Show Reasoning**: false

## Updating the Agent

To update the agent or tools:

1. **Update Agent**: Modify `ibm-orchestrate-agent.yaml` and re-import:
   ```powershell
   orchestrate agents import --file ibm-orchestrate-agent.yaml
   ```

2. **Update Tools**: Modify `product-catalog-api-openapi.yaml` and re-import:
   ```powershell
   orchestrate tools import --kind openapi --file product-catalog-api-openapi.yaml
   ```

## Troubleshooting

### Error: "Missing option '--kind'"
- **Solution**: Use `--kind openapi` when importing tools
- **Correct command**: `orchestrate tools import --kind openapi --file product-catalog-api-openapi.yaml`

### Error: "Field 'spec_version' not provided"
- Ensure the agent YAML file has `spec_version: v1` at the top
- Check YAML formatting (proper indentation)

### Error: "Input should be a valid string" for tools
- This means tools are defined inline instead of being referenced by name
- Tools must be imported separately first using OpenAPI spec
- Agent YAML should only reference tool names as strings (e.g., `get_products`)

### Error: "Input should be an instance of BaseTool"
- Tools must be registered in IBM Orchestrate before being referenced
- Import the OpenAPI specification file before importing the agent

### Tool Import Fails
- Verify the API endpoint is accessible
- Check that the OpenAPI spec is valid (use an OpenAPI validator)
- Ensure all required fields are present (operationId, paths, etc.)

### Agent Cannot Find Tools
- Verify tools are imported: `orchestrate tools list`
- Ensure tool names in agent YAML match the operationId in OpenAPI spec exactly
- Tool names are case-sensitive (use `get_products`, not `Get Products`)

## Testing the Agent

After deployment, test the agent with sample queries:

1. **List all products**:
   ```
   "Show me all available IBM products"
   ```

2. **Search for products**:
   ```
   "Find products related to Cloud Pak"
   "Search for product 5737-H33"
   ```

3. **Get specific product**:
   ```
   "Get details for product code 5737-H33"
   ```

## API Endpoint Configuration

The tools are configured to use:
```
https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com
```

To change the API endpoint:
1. Update the `servers.url` field in `product-catalog-api-openapi.yaml`
2. Re-import the tools: `orchestrate tools import --kind openapi --file product-catalog-api-openapi.yaml`

## Quick Reference

### Complete Deployment Commands

```powershell
# Step 1: Import tools from OpenAPI spec
orchestrate tools import --kind openapi --file product-catalog-api-openapi.yaml

# Step 2: Verify tools
orchestrate tools list

# Step 3: Import agent
orchestrate agents import --file ibm-orchestrate-agent.yaml

# Step 4: Verify agent
orchestrate agents list
```

### Tool Names (operationId in OpenAPI)
- `get_products` - GET /products
- `search_products` - GET /products/search
- `get_product` - GET /products/{SLC_CODE}

## Support

For issues or questions:
- Check the [Troubleshooting Guide](../troubleshooting/TROUBLESHOOTING.md)
- Review IBM Orchestrate documentation
- Contact the development team