#!/usr/bin/env python3
"""
LinkedIn Posts MCP - AI News to LinkedIn Posts Generator

This script fetches the latest AI news and generates professional bilingual
LinkedIn posts using OpenAI's API with the Model Completion Protocol (MCP).
"""

import os
import json
import sys
import subprocess
import tempfile
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class NewsFetcher:
    """Handles fetching AI news using MCP server."""
    
    def __init__(self):
        self.mcp_server_path = os.getenv('MCP_SERVER_PATH', 'mcp-server-news')
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def search_news_with_mcp(self, query: str = "latest artificial intelligence AI news") -> List[Dict]:
        """Search for AI news using MCP server."""
        try:
            print(f"Searching for news with MCP: '{query}'")
            
            # Create a temporary MCP request file
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search_news",
                    "arguments": {
                        "query": query,
                        "max_results": 2,
                        "language": "en"
                    }
                }
            }
            
            # Try to use MCP server if available
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(mcp_request, f)
                    temp_file = f.name
                
                # Execute MCP server command
                result = subprocess.run(
                    [self.mcp_server_path, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                os.unlink(temp_file)  # Clean up temp file
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    if 'result' in response and 'content' in response['result']:
                        return self._parse_mcp_news_response(response['result']['content'])
                
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
                print(f"MCP server not available or failed: {e}")
                print("Falling back to OpenAI-based news search...")
            
            # Fallback: Use OpenAI to search for recent AI news
            return self._search_news_with_openai(query)
            
        except Exception as e:
            print(f"Error in MCP news search: {e}")
            return []
    
    def _parse_mcp_news_response(self, content: str) -> List[Dict]:
        """Parse MCP server response into article format."""
        try:
            # Try to extract structured data from MCP response
            articles = []
            lines = content.split('\n')
            
            current_article = {}
            for line in lines:
                line = line.strip()
                if line.startswith('Title:') or line.startswith('**Title:'):
                    if current_article:
                        articles.append(current_article)
                    current_article = {'title': line.split(':', 1)[1].strip()}
                elif line.startswith('Summary:') or line.startswith('**Summary:'):
                    current_article['summary'] = line.split(':', 1)[1].strip()
                elif line.startswith('URL:') or line.startswith('**URL:'):
                    current_article['url'] = line.split(':', 1)[1].strip()
                elif line.startswith('http') and 'url' not in current_article:
                    current_article['url'] = line
            
            if current_article and 'title' in current_article:
                articles.append(current_article)
            
            return articles[:2]  # Return top 2 articles
            
        except Exception as e:
            print(f"Error parsing MCP response: {e}")
            return []
    
    def _search_news_with_openai(self, query: str) -> List[Dict]:
        """Fallback: Use OpenAI to search for and summarize recent AI news."""
        try:
            print("Using OpenAI to search for recent AI news...")
            
            search_prompt = f"""
You are a news researcher. Find the 2 most recent and relevant AI/artificial intelligence news articles.

Search query: "{query}"

Please provide the information in this exact JSON format:
{{
  "articles": [
    {{
      "title": "Article title here",
      "summary": "Brief summary of the article content",
      "url": "Article URL if available, or 'N/A' if not"
    }}
  ]
}}

Focus on:
- Recent developments in AI, machine learning, or artificial intelligence
- Major company announcements (OpenAI, Google, Microsoft, etc.)
- Breakthrough research or new AI models
- Industry trends and analysis

If you cannot find recent articles, provide the most relevant recent AI news you're aware of.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful news researcher who provides accurate, recent information about AI developments."},
                    {"role": "user", "content": search_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                data = json.loads(content)
                articles = data.get('articles', [])
                print(f"Found {len(articles)} articles via OpenAI search")
                return articles
            except json.JSONDecodeError:
                print("Could not parse OpenAI response as JSON, creating fallback article")
                return [{
                    'title': 'Recent AI Developments',
                    'summary': content[:200] + "..." if len(content) > 200 else content,
                    'url': 'N/A'
                }]
                
        except Exception as e:
            print(f"Error in OpenAI news search: {e}")
            return []
    
    def fetch_latest_news(self) -> List[Dict]:
        """Fetch latest AI news using MCP server."""
        print("Fetching latest AI news using MCP...")
        
        articles = self.search_news_with_mcp("latest artificial intelligence AI news developments")
        
        if not articles:
            print("No articles found from MCP search.")
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
- All information must be new, not older than 2 weeks.

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
