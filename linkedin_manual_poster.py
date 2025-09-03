#!/usr/bin/env python3
"""
LinkedIn Manual Poster - Generates posts ready for manual copying to LinkedIn

This script generates LinkedIn posts and formats them for easy manual posting.
It opens the LinkedIn posting page and provides the formatted content.
"""

import os
import json
import webbrowser
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInManualPoster:
    """Handles generating LinkedIn posts for manual posting."""
    
    def __init__(self):
        pass
    
    def format_post_for_linkedin(self, post_data: Dict, language: str = 'en') -> str:
        """Format post data for LinkedIn manual posting."""
        if language == 'es' and 'post_body_es' in post_data:
            post_text = post_data['post_body_es']
        else:
            post_text = post_data.get('post_body_en', '')
        
        if not post_text:
            return "No post content available"
        
        # Clean up the post text
        formatted_post = post_text.strip()
        
        # Add link if available
        if post_data.get('link') and post_data['link'] != 'N/A':
            formatted_post += f"\n\n{post_data['link']}"
        
        return formatted_post
    
    def display_post_options(self, post_data: Dict):
        """Display formatted posts for manual copying."""
        print("=" * 60)
        print("📝 LINKEDIN POSTS READY FOR MANUAL POSTING")
        print("=" * 60)
        print(f"Title: {post_data.get('title', 'N/A')}")
        print(f"Original Link: {post_data.get('link', 'N/A')}")
        print()
        
        # English version
        english_post = self.format_post_for_linkedin(post_data, 'en')
        print("🇺🇸 ENGLISH VERSION:")
        print("-" * 40)
        print(english_post)
        print()
        
        # Spanish version
        spanish_post = self.format_post_for_linkedin(post_data, 'es')
        print("🇪🇸 SPANISH VERSION:")
        print("-" * 40)
        print(spanish_post)
        print()
        
        print("=" * 60)
        print("📋 INSTRUCTIONS:")
        print("1. Copy the post text above")
        print("2. Go to LinkedIn and create a new post")
        print("3. Paste the content")
        print("4. Add any additional hashtags or mentions")
        print("5. Publish your post")
        print("=" * 60)
    
    def open_linkedin_posting(self):
        """Open LinkedIn posting page in browser."""
        try:
            webbrowser.open('https://www.linkedin.com/feed/')
            print("🌐 LinkedIn opened in your browser")
            print("You can now create a new post and paste the content above")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("Please manually go to: https://www.linkedin.com/feed/")
    
    def save_to_clipboard_format(self, post_data: Dict, language: str = 'en'):
        """Save post to a file in clipboard-friendly format."""
        post_text = self.format_post_for_linkedin(post_data, language)
        
        filename = f"linkedin_post_{language}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(post_text)
            print(f"📄 Post saved to: {filename}")
            print("You can copy the content from this file")
        except Exception as e:
            print(f"❌ Error saving file: {e}")


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
    """Main entry point for manual LinkedIn posting."""
    print("=== LinkedIn Manual Poster ===\n")
    
    # Load post data
    post_data = load_post_data()
    if not post_data:
        return
    
    # Initialize poster
    poster = LinkedInManualPoster()
    
    # Display formatted posts
    poster.display_post_options(post_data)
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Open LinkedIn in browser")
    print("2. Save English post to file")
    print("3. Save Spanish post to file")
    print("4. Save both posts to files")
    print("5. Just display (already done)")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            poster.open_linkedin_posting()
        elif choice == '2':
            poster.save_to_clipboard_format(post_data, 'en')
        elif choice == '3':
            poster.save_to_clipboard_format(post_data, 'es')
        elif choice == '4':
            poster.save_to_clipboard_format(post_data, 'en')
            poster.save_to_clipboard_format(post_data, 'es')
        elif choice == '5':
            print("✅ Posts displayed above. Ready for manual posting!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Manual posting cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
