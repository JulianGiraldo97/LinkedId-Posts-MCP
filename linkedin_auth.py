#!/usr/bin/env python3
"""
LinkedIn OAuth Authentication Helper

This script helps you generate a LinkedIn access token using your Client ID and Client Secret.
It implements the OAuth 2.0 authorization code flow for LinkedIn API.
"""

import os
import json
import webbrowser
import urllib.parse
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInAuth:
    """Handles LinkedIn OAuth authentication flow."""
    
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8080/callback')
        
        if not self.client_id:
            raise ValueError("LINKEDIN_CLIENT_ID environment variable is required")
        if not self.client_secret:
            raise ValueError("LINKEDIN_CLIENT_SECRET environment variable is required")
    
    def generate_auth_url(self) -> str:
        """Generate LinkedIn authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': 'random_state_string',
            'scope': 'w_member_social,r_organization_social'
        }
        
        auth_url = 'https://www.linkedin.com/oauth/v2/authorization?' + urllib.parse.urlencode(params)
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Optional[Dict]:
        """Exchange authorization code for access token."""
        token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error exchanging code for token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_user_profile(self, access_token: str) -> Optional[Dict]:
        """Get user profile to verify token works."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.get(
                'https://api.linkedin.com/rest/people/~',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def get_company_pages(self, access_token: str) -> Optional[list]:
        """Get list of company pages the user can post to."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            # Get user's organizations
            response = requests.get(
                'https://api.linkedin.com/rest/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting company pages: {e}")
            return None


def main():
    """Main authentication flow."""
    print("=== LinkedIn OAuth Authentication ===\n")
    
    # Check for required environment variables
    if not os.getenv('LINKEDIN_CLIENT_ID'):
        print("❌ Error: LINKEDIN_CLIENT_ID environment variable is required.")
        print("Please set it in your .env file.")
        return
    
    if not os.getenv('LINKEDIN_CLIENT_SECRET'):
        print("❌ Error: LINKEDIN_CLIENT_SECRET environment variable is required.")
        print("Please set it in your .env file.")
        return
    
    try:
        auth = LinkedInAuth()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return
    
    print("🔗 Step 1: Opening LinkedIn authorization page...")
    auth_url = auth.generate_auth_url()
    print(f"Authorization URL: {auth_url}")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except Exception:
        print("⚠️  Could not open browser automatically")
        print("Please copy and paste the URL above into your browser")
    
    print("\n📋 Step 2: Authorize the application")
    print("1. You'll be redirected to LinkedIn")
    print("2. Log in and authorize the application")
    print("3. You'll be redirected to a callback URL")
    print("4. Copy the 'code' parameter from the callback URL")
    
    print(f"\n🔗 Callback URL: {auth.redirect_uri}")
    print("Look for: http://localhost:8080/callback?code=XXXXX&state=random_state_string")
    
    # Get authorization code from user
    print("\n📝 Step 3: Enter the authorization code")
    authorization_code = input("Enter the authorization code from the callback URL: ").strip()
    
    if not authorization_code:
        print("❌ No authorization code provided. Exiting.")
        return
    
    print("\n🔄 Step 4: Exchanging code for access token...")
    token_data = auth.exchange_code_for_token(authorization_code)
    
    if not token_data:
        print("❌ Failed to get access token. Please try again.")
        return
    
    access_token = token_data.get('access_token')
    expires_in = token_data.get('expires_in', 'Unknown')
    
    print(f"✅ Successfully obtained access token!")
    print(f"Token expires in: {expires_in} seconds")
    
    # Verify token works
    print("\n🔍 Step 5: Verifying token...")
    profile = auth.get_user_profile(access_token)
    
    if profile:
        print(f"✅ Token verified! Logged in as: {profile.get('firstName', '')} {profile.get('lastName', '')}")
    else:
        print("⚠️  Could not verify token, but it was generated successfully")
    
    # Get company pages
    print("\n🏢 Step 6: Getting company pages...")
    companies = auth.get_company_pages(access_token)
    
    if companies and 'elements' in companies:
        print("✅ Available company pages:")
        for company in companies['elements']:
            org_id = company.get('organizationalTarget', '')
            if org_id:
                print(f"  - Company ID: {org_id}")
    else:
        print("⚠️  Could not retrieve company pages")
        print("You may need to manually find your company ID")
    
    # Save token to .env file
    print("\n💾 Step 7: Saving credentials...")
    
    # Read current .env file
    env_file = '.env'
    env_content = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Update or add access token
    updated = False
    for i, line in enumerate(env_content):
        if line.startswith('LINKEDIN_ACCESS_TOKEN='):
            env_content[i] = f'LINKEDIN_ACCESS_TOKEN={access_token}\n'
            updated = True
            break
    
    if not updated:
        env_content.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    print(f"✅ Access token saved to {env_file}")
    
    print("\n🎉 Authentication complete!")
    print("You can now use the LinkedIn posting functionality.")
    print("\nNext steps:")
    print("1. Find your company ID from your LinkedIn company page URL")
    print("2. Add LINKEDIN_COMPANY_ID to your .env file")
    print("3. Run: python post_to_linkedin.py")


if __name__ == "__main__":
    main()
