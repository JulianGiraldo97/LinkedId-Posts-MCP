#!/usr/bin/env python3
"""
LinkedIn Posts MCP - AI News to LinkedIn Posts Generator

This script fetches the latest AI news and generates professional bilingual
LinkedIn posts using OpenAI's API with the Model Completion Protocol (MCP).
"""

import os
import json
import sys
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class NewsFetcher:
    """Handles fetching AI news from various sources."""
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.google_news_rss = "https://news.google.com/rss/search?q=artificial+intelligence+AI&hl=en-US&gl=US&ceid=US:en"
    
    def fetch_from_newsapi(self) -> List[Dict]:
        """Fetch AI news from NewsAPI."""
        if not self.newsapi_key:
            print("Warning: NEWSAPI_KEY not found. Skipping NewsAPI.")
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'artificial intelligence OR AI OR machine learning',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'apiKey': self.newsapi_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', [])[:2]:  # Top 2 articles
                if article.get('title') and article.get('description'):
                    articles.append({
                        'title': article['title'],
                        'summary': article['description'],
                        'url': article['url']
                    })
            
            return articles
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    def fetch_from_google_news(self) -> List[Dict]:
        """Fetch AI news from Google News RSS."""
        try:
            feed = feedparser.parse(self.google_news_rss)
            articles = []
            
            for entry in feed.entries[:2]:  # Top 2 articles
                if entry.get('title') and entry.get('summary'):
                    articles.append({
                        'title': entry.title,
                        'summary': entry.summary,
                        'url': entry.link
                    })
            
            return articles
        except Exception as e:
            print(f"Error fetching from Google News: {e}")
            return []
    
    def fetch_latest_news(self) -> List[Dict]:
        """Fetch latest AI news from available sources."""
        print("Fetching latest AI news...")
        
        # Try NewsAPI first, then fallback to Google News
        articles = self.fetch_from_newsapi()
        
        if not articles:
            print("Falling back to Google News RSS...")
            articles = self.fetch_from_google_news()
        
        if not articles:
            print("No articles found from any source.")
            return []
        
        print(f"Found {len(articles)} articles")
        return articles


class LinkedInPostGenerator:
    """Handles generating LinkedIn posts using OpenAI with MCP protocol."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.mcp_prompt = """
You are an AI assistant integrated via the Model Completion Protocol (MCP).

Goal: Generate professional, bilingual LinkedIn posts for a company page based on the latest AI news.

Context:
- This MCP call will receive recent AI-related news articles as input.
- Your task is to:
  1. Read and understand the top 1–2 news articles.
  2. Summarize the core insight or key takeaway.
  3. Generate a concise, company-branded LinkedIn post in **two languages**:
     - English
     - Spanish (localized, not just literal translation)
  4. Include the original article link and relevant hashtags in both versions.
  5. Ensure the tone is informative, professional, and suitable for a company audience.

Constraints:
- Avoid hype or speculative language.
- Posts must be immediately ready to publish — polished and fluent in both languages.
- Posts should not exceed 120 words per language.
- If multiple articles are provided, focus on the most relevant one.

Input format:
{
  "articles": [
    {
      "title": "...",
      "summary": "...",
      "url": "..."
    }
  ]
}

Output format:
{
  "title": "...",
  "post_body_en": "...",
  "post_body_es": "...",
  "link": "..."
}

Task: Write both English and Spanish versions of the LinkedIn post using the article content provided.
"""
    
    def construct_mcp_payload(self, articles: List[Dict]) -> Dict:
        """Construct MCP payload for OpenAI."""
        return {
            "articles": articles
        }
    
    def generate_post(self, articles: List[Dict]) -> Optional[Dict]:
        """Generate LinkedIn post using OpenAI with MCP protocol."""
        if not articles:
            print("No articles provided for post generation.")
            return None
        
        payload = self.construct_mcp_payload(articles)
        
        try:
            print("Generating LinkedIn post with OpenAI...")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self.mcp_prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, indent=2)
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                print("Warning: OpenAI response is not valid JSON. Returning raw content.")
                return {
                    "title": "AI News Update",
                    "post_body_en": content,
                    "post_body_es": "Error: Could not parse Spanish version",
                    "link": articles[0].get('url', '')
                }
                
        except Exception as e:
            print(f"Error generating post with OpenAI: {e}")
            return None


class LinkedInMCP:
    """Main class that orchestrates the entire process."""
    
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.post_generator = LinkedInPostGenerator()
    
    def run(self) -> Optional[Dict]:
        """Run the complete process: fetch news -> generate post -> output result."""
        print("=== LinkedIn Posts MCP - AI News Generator ===\n")
        
        # Step 1: Fetch latest AI news
        articles = self.news_fetcher.fetch_latest_news()
        if not articles:
            print("No articles found. Exiting.")
            return None
        
        # Step 2: Generate LinkedIn post
        post_data = self.post_generator.generate_post(articles)
        if not post_data:
            print("Failed to generate post. Exiting.")
            return None
        
        # Step 3: Output results
        self.output_results(post_data)
        
        return post_data
    
    def output_results(self, post_data: Dict):
        """Output the generated LinkedIn post."""
        print("\n=== Generated LinkedIn Post ===")
        print(f"Title: {post_data.get('title', 'N/A')}")
        print(f"\nEnglish Version:")
        print(post_data.get('post_body_en', 'N/A'))
        print(f"\nSpanish Version:")
        print(post_data.get('post_body_es', 'N/A'))
        print(f"\nLink: {post_data.get('link', 'N/A')}")
        
        # Save to JSON file
        output_file = "linkedin_post.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
            print(f"\nPost saved to: {output_file}")
        except Exception as e:
            print(f"Error saving to file: {e}")


def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)
    
    # Initialize and run the MCP
    mcp = LinkedInMCP()
    result = mcp.run()
    
    if result:
        print("\n✅ LinkedIn post generated successfully!")
    else:
        print("\n❌ Failed to generate LinkedIn post.")
        sys.exit(1)


if __name__ == "__main__":
    main()
