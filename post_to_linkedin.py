#!/usr/bin/env python3
"""
Complete LinkedIn Posting Pipeline

This script combines news generation and LinkedIn posting into one workflow.
It generates AI news posts and immediately posts them to your LinkedIn company page.
"""

import os
import sys
import json
from linkedin_mcp import LinkedInMCP
from linkedin_poster import LinkedInPoster, load_post_data

def main():
    """Main workflow: Generate news post and post to LinkedIn."""
    print("=== Complete LinkedIn Posting Pipeline ===\n")
    
    # Step 1: Generate the LinkedIn post
    print("🔄 Step 1: Generating AI news post...")
    mcp = LinkedInMCP()
    post_data = mcp.run()
    
    if not post_data:
        print("❌ Failed to generate post. Exiting.")
        sys.exit(1)
    
    print("✅ Post generated successfully!")
    
    # Step 2: Post to LinkedIn
    print("\n🔄 Step 2: Posting to LinkedIn...")
    
    # Check for LinkedIn credentials
    if not os.getenv('LINKEDIN_ACCESS_TOKEN'):
        print("❌ Error: LINKEDIN_ACCESS_TOKEN environment variable is required.")
        print("Please set it in your .env file to enable LinkedIn posting.")
        print("For now, the post has been saved to linkedin_post.json")
        sys.exit(0)
    
    if not os.getenv('LINKEDIN_COMPANY_ID'):
        print("❌ Error: LINKEDIN_COMPANY_ID environment variable is required.")
        print("Please set it in your .env file to enable LinkedIn posting.")
        print("For now, the post has been saved to linkedin_post.json")
        sys.exit(0)
    
    # Initialize LinkedIn poster
    try:
        poster = LinkedInPoster()
    except ValueError as e:
        print(f"❌ LinkedIn Configuration Error: {e}")
        print("For now, the post has been saved to linkedin_post.json")
        sys.exit(1)
    
    # Ask user which version to post
    print("\nWhich version would you like to post?")
    print("1. English only")
    print("2. Spanish only") 
    print("3. Both versions")
    print("4. Skip posting (post saved to linkedin_post.json)")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
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
                
        elif choice == '4':
            print("\n✅ Post saved to linkedin_post.json. You can post it manually later.")
            
        else:
            print("❌ Invalid choice. Post saved to linkedin_post.json.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Process cancelled by user.")
        print("✅ Post saved to linkedin_post.json")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("✅ Post saved to linkedin_post.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
