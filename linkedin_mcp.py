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
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class MediumScraper:
    """Handles scraping AI news from Medium.com"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_ai_articles(self, max_results: int = 5) -> List[Dict]:
        """Search for AI-related articles on Medium"""
        try:
            print("Searching Medium for AI articles...")
            
            # Medium search URL for AI articles
            search_urls = [
                "https://medium.com/tag/artificial-intelligence",
                "https://medium.com/tag/machine-learning", 
                "https://medium.com/tag/ai",
                "https://medium.com/tag/chatgpt",
                "https://medium.com/tag/openai"
            ]
            
            articles = []
            
            for url in search_urls:
                try:
                    print(f"Scraping: {url}")
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    found_articles = self._parse_medium_articles(soup)
                    articles.extend(found_articles)
                    
                    # Avoid rate limiting
                    time.sleep(1)
                    
                    if len(articles) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_articles = self._remove_duplicates(articles)
            return unique_articles[:max_results]
            
        except Exception as e:
            print(f"Error in Medium search: {e}")
            return []
    
    def _parse_medium_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Medium articles from HTML"""
        articles = []
        
        try:
            # Look for article containers (Medium's structure may vary)
            article_selectors = [
                'article',
                '[data-testid="post-preview"]',
                '.postArticle',
                '.streamItem',
                'div[role="button"]'
            ]
            
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    break
            
            for element in elements[:5]:  # Limit to 5 per page
                try:
                    article_data = self._extract_article_data(element)
                    if article_data and article_data.get('title'):
                        articles.append(article_data)
                except Exception as e:
                    print(f"Error parsing article element: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing Medium articles: {e}")
        
        return articles
    
    def _extract_article_data(self, element) -> Optional[Dict]:
        """Extract article data from a single element"""
        try:
            # Try to find title
            title_selectors = [
                'h1', 'h2', 'h3',
                '[data-testid="post-preview-title"]',
                '.graf--title',
                '.postArticle-title'
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                return None
            
            # Try to find link
            link = None
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    link = f"https://medium.com{href}"
                elif href.startswith('http'):
                    link = href
            
            # Try to find summary/description
            summary_selectors = [
                'p',
                '[data-testid="post-preview-description"]',
                '.graf--p',
                '.postArticle-content'
            ]
            
            summary = None
            for selector in summary_selectors:
                summary_elem = element.select_one(selector)
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                    if len(summary) > 50:  # Only use substantial summaries
                        break
            
            # Clean up summary
            if summary and len(summary) > 200:
                summary = summary[:200] + "..."
            
            return {
                'title': title,
                'summary': summary or f"Read more about {title}",
                'url': link or 'https://medium.com'
            }
            
        except Exception as e:
            print(f"Error extracting article data: {e}")
            return None
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles

class NewsFetcher:
    """Handles fetching AI news from Medium and other sources."""
    
    def __init__(self):
        self.mcp_server_path = os.getenv('MCP_SERVER_PATH', 'mcp-server-news')
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.medium_scraper = MediumScraper()
    
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
        """Fetch latest AI news from Medium."""
        print("Fetching latest AI news from Medium...")
        
        # Try Medium scraping first
        articles = self.medium_scraper.search_ai_articles(max_results=3)
        
        if articles:
            print(f"Found {len(articles)} articles from Medium")
            return articles
        
        # Fallback to MCP if Medium fails
        print("Medium scraping failed, trying MCP fallback...")
        articles = self.search_news_with_mcp("latest artificial intelligence AI news developments")
        
        if not articles:
            print("No articles found from any source.")
            return []
        
        print(f"Found {len(articles)} articles from MCP fallback")
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
