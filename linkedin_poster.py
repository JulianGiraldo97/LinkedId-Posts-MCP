#!/usr/bin/env python3
"""
LinkedIn Poster - Posts generated content to LinkedIn Company Page

This script reads the generated LinkedIn post JSON and posts it directly
to your LinkedIn company page using the LinkedIn API.
"""

import os
import json
import sys
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInPoster:
    """Handles posting content to LinkedIn company page."""
    
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.company_id = os.getenv('LINKEDIN_COMPANY_ID')
        self.api_version = '202401'
        self.base_url = f'https://api.linkedin.com/rest/{self.api_version}'
        
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN environment variable is required")
        if not self.company_id:
            raise ValueError("LINKEDIN_COMPANY_ID environment variable is required")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for LinkedIn API requests."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def post_to_company_page(self, post_data: Dict, language: str = 'en') -> bool:
        """Post content to LinkedIn company page."""
        try:
            # Determine which post body to use based on language
            if language == 'es' and 'post_body_es' in post_data:
                post_text = post_data['post_body_es']
            else:
                post_text = post_data.get('post_body_en', '')
            
            if not post_text:
                print(f"Error: No post content found for language '{language}'")
                return False
            
            # Prepare the LinkedIn API payload
            linkedin_payload = {
                "author": f"urn:li:organization:{self.company_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add link if available
            if post_data.get('link') and post_data['link'] != 'N/A':
                linkedin_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                linkedin_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": post_text[:200] + "..." if len(post_text) > 200 else post_text
                        },
                        "media": post_data['link'],
                        "title": {
                            "text": post_data.get('title', 'AI News Update')
                        }
                    }
                ]
            
            print(f"Posting to LinkedIn company page (ID: {self.company_id})...")
            print(f"Language: {language}")
            print(f"Post preview: {post_text[:100]}...")
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self.get_headers(),
                json=linkedin_payload,
                timeout=30
            )
            
            if response.status_code == 201:
                post_id = response.headers.get('X-RestLi-Id', 'Unknown')
                print(f"✅ Successfully posted to LinkedIn!")
                print(f"Post ID: {post_id}")
                print(f"View your post: https://www.linkedin.com/feed/update/{post_id}")
                return True
            else:
                print(f"❌ Failed to post to LinkedIn")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            return False
    
    def post_both_languages(self, post_data: Dict) -> Dict[str, bool]:
        """Post both English and Spanish versions."""
        results = {}
        
        print("=== Posting English Version ===")
        results['english'] = self.post_to_company_page(post_data, 'en')
        
        print("\n=== Posting Spanish Version ===")
        results['spanish'] = self.post_to_company_page(post_data, 'es')
        
        return results


def load_post_data(json_file: str = 'linkedin_post.json') -> Optional[Dict]:
    """Load post data from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {json_file} not found. Please run linkedin_mcp.py first to generate a post.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {json_file}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading {json_file}: {e}")
        return None


def main():
    """Main entry point for LinkedIn posting."""
    print("=== LinkedIn Company Page Poster ===\n")
    
    # Check for required environment variables
    if not os.getenv('LINKEDIN_ACCESS_TOKEN'):
        print("❌ Error: LINKEDIN_ACCESS_TOKEN environment variable is required.")
        print("Please set it in your .env file.")
        sys.exit(1)
    
    if not os.getenv('LINKEDIN_COMPANY_ID'):
        print("❌ Error: LINKEDIN_COMPANY_ID environment variable is required.")
        print("Please set it in your .env file.")
        sys.exit(1)
    
    # Load post data
    post_data = load_post_data()
    if not post_data:
        sys.exit(1)
    
    print("📄 Loaded post data:")
    print(f"Title: {post_data.get('title', 'N/A')}")
    print(f"Link: {post_data.get('link', 'N/A')}")
    
    # Initialize poster
    try:
        poster = LinkedInPoster()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    
    # Ask user which version to post
    print("\nWhich version would you like to post?")
    print("1. English only")
    print("2. Spanish only") 
    print("3. Both versions")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            success = poster.post_to_company_page(post_data, 'en')
            if success:
                print("\n🎉 English post published successfully!")
            else:
                print("\n❌ Failed to publish English post.")
                
        elif choice == '2':
            success = poster.post_to_company_page(post_data, 'es')
            if success:
                print("\n🎉 Spanish post published successfully!")
            else:
                print("\n❌ Failed to publish Spanish post.")
                
        elif choice == '3':
            results = poster.post_both_languages(post_data)
            english_success = results.get('english', False)
            spanish_success = results.get('spanish', False)
            
            print(f"\n📊 Posting Results:")
            print(f"English: {'✅ Success' if english_success else '❌ Failed'}")
            print(f"Spanish: {'✅ Success' if spanish_success else '❌ Failed'}")
            
            if english_success and spanish_success:
                print("\n🎉 Both posts published successfully!")
            elif english_success or spanish_success:
                print("\n⚠️  One post published successfully.")
            else:
                print("\n❌ Both posts failed to publish.")
        else:
            print("❌ Invalid choice. Please run the script again and select 1, 2, or 3.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Posting cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
