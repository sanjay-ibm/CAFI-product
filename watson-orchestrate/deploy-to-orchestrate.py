#!/usr/bin/env python3
"""
Watson Orchestrate Deployment Script
Deploys the Product Search skill to Watson Orchestrate
"""

import os
import sys
import json
import requests
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OrchestrateDeployer:
    """Deploy skills to Watson Orchestrate"""
    
    def __init__(self):
        self.api_key = os.getenv('ORCHESTRATE_API_KEY')
        self.api_url = os.getenv('ORCHESTRATE_API_URL', 'https://api.orchestrate.ibm.com')
        self.tenant_id = os.getenv('ORCHESTRATE_TENANT_ID')
        self.region = os.getenv('ORCHESTRATE_REGION', 'us-south')
        
        if not self.api_key:
            raise ValueError("ORCHESTRATE_API_KEY not found in environment variables")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.tenant_id:
            self.headers['X-Tenant-ID'] = self.tenant_id
    
    def load_openapi_spec(self, spec_path: str) -> Dict[str, Any]:
        """Load OpenAPI specification from YAML file"""
        print(f"📖 Loading OpenAPI spec from {spec_path}...")
        
        with open(spec_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        print(f"✅ Loaded OpenAPI spec: {spec['info']['title']} v{spec['info']['version']}")
        return spec
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load deployment configuration"""
        print(f"📖 Loading configuration from {config_path}...")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Loaded configuration for skill: {config['skill']['name']}")
        return config
    
    def validate_api_connection(self) -> bool:
        """Validate connection to Watson Orchestrate API"""
        print(f"🔌 Validating connection to {self.api_url}...")
        
        try:
            response = requests.get(
                f"{self.api_url}/v1/health",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Successfully connected to Watson Orchestrate API")
                return True
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to Watson Orchestrate API: {e}")
            return False
    
    def create_skill(self, openapi_spec: Dict[str, Any], config: Dict[str, Any]) -> Optional[str]:
        """Create a new skill in Watson Orchestrate"""
        print(f"\n🚀 Creating skill: {config['skill']['name']}...")
        
        skill_payload = {
            "name": config['skill']['name'],
            "description": config['skill']['description'],
            "version": config['skill']['version'],
            "category": config['skill']['category'],
            "tags": config['skill']['tags'],
            "openapi_spec": openapi_spec,
            "base_url": config['api']['base_url'],
            "authentication": config['api']['authentication']
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/v1/skills",
                headers=self.headers,
                json=skill_payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                skill_data = response.json()
                skill_id = skill_data.get('id') or skill_data.get('skill_id')
                print(f"✅ Skill created successfully!")
                print(f"   Skill ID: {skill_id}")
                return skill_id
            else:
                print(f"❌ Failed to create skill: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating skill: {e}")
            return None
    
    def update_skill(self, skill_id: str, openapi_spec: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Update an existing skill in Watson Orchestrate"""
        print(f"\n🔄 Updating skill: {skill_id}...")
        
        skill_payload = {
            "name": config['skill']['name'],
            "description": config['skill']['description'],
            "version": config['skill']['version'],
            "category": config['skill']['category'],
            "tags": config['skill']['tags'],
            "openapi_spec": openapi_spec,
            "base_url": config['api']['base_url'],
            "authentication": config['api']['authentication']
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/v1/skills/{skill_id}",
                headers=self.headers,
                json=skill_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Skill updated successfully!")
                return True
            else:
                print(f"❌ Failed to update skill: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error updating skill: {e}")
            return False
    
    def list_skills(self) -> Optional[list]:
        """List all skills in Watson Orchestrate"""
        print("\n📋 Listing existing skills...")
        
        try:
            response = requests.get(
                f"{self.api_url}/v1/skills",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                skills = response.json().get('skills', [])
                print(f"✅ Found {len(skills)} existing skills")
                for skill in skills:
                    print(f"   - {skill.get('name')} (ID: {skill.get('id')})")
                return skills
            else:
                print(f"⚠️  Failed to list skills: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing skills: {e}")
            return None
    
    def find_skill_by_name(self, name: str) -> Optional[str]:
        """Find a skill by name and return its ID"""
        skills = self.list_skills()
        if skills:
            for skill in skills:
                if skill.get('name') == name:
                    return skill.get('id')
        return None
    
    def deploy(self, spec_path: str, config_path: str, update: bool = False) -> bool:
        """Main deployment function"""
        print("=" * 70)
        print("🤖 Watson Orchestrate Skill Deployment")
        print("=" * 70)
        
        # Load files
        try:
            openapi_spec = self.load_openapi_spec(spec_path)
            config = self.load_config(config_path)
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False
        
        # Validate connection
        if not self.validate_api_connection():
            print("\n⚠️  Warning: Could not validate API connection")
            print("   Proceeding anyway, but deployment may fail...")
        
        # Check if skill already exists
        skill_name = config['skill']['name']
        existing_skill_id = self.find_skill_by_name(skill_name)
        
        if existing_skill_id and update:
            # Update existing skill
            success = self.update_skill(existing_skill_id, openapi_spec, config)
        elif existing_skill_id and not update:
            print(f"\n⚠️  Skill '{skill_name}' already exists (ID: {existing_skill_id})")
            print("   Use --update flag to update the existing skill")
            return False
        else:
            # Create new skill
            skill_id = self.create_skill(openapi_spec, config)
            success = skill_id is not None
        
        if success:
            print("\n" + "=" * 70)
            print("✅ Deployment completed successfully!")
            print("=" * 70)
            print(f"\n📝 Next steps:")
            print(f"   1. Log in to Watson Orchestrate: {self.api_url}")
            print(f"   2. Navigate to Skills section")
            print(f"   3. Find your skill: {skill_name}")
            print(f"   4. Test the skill with sample queries")
            print(f"   5. Add the skill to your assistant or workflow")
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ Deployment failed!")
            print("=" * 70)
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Deploy Product Search skill to Watson Orchestrate'
    )
    parser.add_argument(
        '--spec',
        default='watson-orchestrate/product-search-skill.yaml',
        help='Path to OpenAPI specification file'
    )
    parser.add_argument(
        '--config',
        default='watson-orchestrate/orchestrate-config.json',
        help='Path to deployment configuration file'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update existing skill if it already exists'
    )
    
    args = parser.parse_args()
    
    # Validate file paths
    if not Path(args.spec).exists():
        print(f"❌ OpenAPI spec file not found: {args.spec}")
        sys.exit(1)
    
    if not Path(args.config).exists():
        print(f"❌ Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Deploy
    try:
        deployer = OrchestrateDeployer()
        success = deployer.deploy(args.spec, args.config, args.update)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob
