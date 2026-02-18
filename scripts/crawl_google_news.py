#!/usr/bin/env python3
"""
Google News Semiconductor Crawler
Crawls Google News semiconductor topic page and saves articles to JSON.
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse, unquote
import re


def clean_google_news_url(url):
    """
    Clean Google News redirect URLs to get the actual article URL.
    Google News uses redirect URLs like: ./articles/...
    """
    if url.startswith('./articles/'):
        # Extract the actual URL from Google's redirect
        # The actual implementation would need to handle Google's URL structure
        return url
    return url


def get_google_news_articles():
    """
    Crawl Google News semiconductor topic page.
    Returns a list of article dictionaries.
    """
    articles = []
    
    # Google News semiconductor topic URL
    url = "https://news.google.com/topics/CAAqKAgKIiJDQkFTRXdvS0wyMHZNRGh0YUROclpCSUZaVzR0UjBJb0FBUAE?hl=en-US&gl=US&ceid=US%3Aen"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Try finding article elements by common Google News patterns
        # Google News uses various class names and structures
        
        # Look for article containers - Google News uses 'article' tags
        article_elements = soup.find_all('article')
        print(f"  Found {len(article_elements)} article elements")
        
        if not article_elements:
            # Fallback: Look for links that might be articles
            # Google News article links often contain '/articles/'
            all_links = soup.find_all('a', href=True)
            print(f"  Found {len(all_links)} total links, filtering for articles...")
            
            seen_titles = set()
            
            for link in all_links:
                href = link.get('href', '')
                
                # Google News article links typically start with ./articles/
                if './read/' in href or '/read/' in href:
                    # Get the link text as title
                    title = link.get_text(strip=True)
                    
                    # Skip empty titles or very short ones
                    if not title or len(title) < 10:
                        continue
                    
                    # Skip duplicates
                    if title in seen_titles:
                        continue
                    
                    seen_titles.add(title)
                    
                    # Try to find the source and time nearby
                    # Look in parent elements
                    source = None
                    time_text = None
                    
                    parent = link.parent
                    if parent:
                        # Try to find source (usually in a nearby element)
                        for sibling in parent.find_all(['span', 'div', 'time']):
                            text = sibling.get_text(strip=True)
                            # Time patterns: "X hours ago", "X days ago", etc.
                            if 'ago' in text.lower() or 'hour' in text.lower() or 'day' in text.lower():
                                time_text = text
                            # Source is usually a publication name
                            elif text and len(text) < 50 and not time_text:
                                # Common publication name patterns
                                if any(word in text for word in ['Times', 'Post', 'News', 'Journal', 'Daily', 
                                                                  'Business', 'Financial', 'Economic', 'Wire',
                                                                  'Reuters', 'Bloomberg', 'CNN', 'BBC', 'CNBC']):
                                    source = text
                    
                    # Build full URL
                    if href.startswith('./'):
                        full_url = urljoin(url, href.replace('./', '/'))
                    elif href.startswith('/'):
                        full_url = urljoin(url, href)
                    else:
                        full_url = href
                    
                    article_data = {
                        'title': title,
                        'url': full_url,
                        'source': source or 'Google News',
                        'crawled_at': datetime.utcnow().isoformat()
                    }
                    
                    if time_text:
                        article_data['published_time'] = time_text
                    
                    articles.append(article_data)
        
        else:
            # Process article elements
            for article in article_elements:
                try:
                    # Find title link
                    title_link = article.find('a', href=True)
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    if not title or len(title) < 10:
                        continue
                    
                    # Build full URL
                    if href.startswith('./'):
                        full_url = urljoin(url, href.replace('./', '/'))
                    elif href.startswith('/'):
                        full_url = urljoin(url, href)
                    else:
                        full_url = href
                    
                    # Find source
                    source = None
                    source_elem = article.find('a', {'data-n-tid': True})
                    if source_elem:
                        source = source_elem.get_text(strip=True)
                    
                    # Find time
                    time_text = None
                    time_elem = article.find('time')
                    if time_elem:
                        time_text = time_elem.get_text(strip=True)
                        if not time_text:
                            time_text = time_elem.get('datetime')
                    
                    article_data = {
                        'title': title,
                        'url': full_url,
                        'source': source or 'Google News',
                        'crawled_at': datetime.utcnow().isoformat()
                    }
                    
                    if time_text:
                        article_data['published_time'] = time_text
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    print(f"  Error processing article: {e}")
                    continue
        
        print(f"  Extracted {len(articles)} articles")
        
    except Exception as e:
        print(f"Error fetching Google News: {e}")
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_articles = []
    for article in articles:
        title = article.get('title', '')
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    return unique_articles


def save_articles(articles, output_file='data/google_news_semiconductor.json'):
    """
    Save articles to a JSON file.
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Add new articles that don't already exist
    all_articles = [article for article in articles]

    
    # Save to file
    output_data = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_articles': len(all_articles),
        'new_articles_today': len(all_articles),
        'source': 'Google News - Semiconductor Topic',
        'articles': all_articles
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(all_articles)} new articles. Total articles: {len(all_articles)}")
    return len(all_articles)


def main():
    """Main function to run the crawler."""
    print("=" * 60)
    print("Google News Semiconductor Crawler")
    print("=" * 60)
    print(f"Time: {datetime.utcnow().isoformat()}\n")
    
    articles = get_google_news_articles()
    
    if articles:
        print(f"\nFound {len(articles)} semiconductor articles from Google News")
        new_count = save_articles(articles)
        print(f"Crawler completed successfully. {new_count} new articles added.")
    else:
        print("No articles found. This might be due to:")
        print("1. Google News structure changes")
        print("2. Network issues or rate limiting")
        print("3. JavaScript-rendered content (may need Selenium)")
        print("\nNote: Google News is heavily JavaScript-based.")
        print("Consider using Selenium or Playwright for better results.")
        # Still create/update the file to show the crawl was attempted
        save_articles([])


if __name__ == "__main__":
    main()

