#!/usr/bin/env python3
"""
Google News Semiconductor Crawler
Crawls Google News semiconductor topic page and saves articles to JSON.

Google News HTML Structure:
- Article links: <a href="./read/...">Title</a>
- Timestamps: <time class="hvbAAd" datetime="2026-02-17T05:34:00Z">2 days ago</time>
  * datetime attribute contains ISO format timestamp
  * text content shows human-readable relative time
- Both are typically in the same parent container
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
    
    Note: Google News uses this structure for timestamps:
    <time class="hvbAAd" datetime="2026-02-17T05:34:00Z">2 days ago</time>
    - datetime attribute: ISO format timestamp
    - text content: Human-readable relative time
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
                    print(f"\n  📰 Processing: {title[:60]}...")
                    
                    # Try to find the source and time nearby
                    # Look in parent elements
                    source = None
                    time_text = None
                    
                    parent = link.parent
                    if parent:
                        # The <time> element might be in parent, grandparent, or great-grandparent
                        # Structure: <time class="hvbAAd" datetime="2026-02-17T05:34:00Z">2 days ago</time>
                        
                        # Build list of ancestors to search (go up 5 levels)
                        search_elements = []
                        current = parent
                        for _ in range(5):  # Search up to 5 levels up
                            if current:
                                search_elements.append(current)
                                current = current.parent
                            else:
                                break
                        
                        # Search each ancestor for <time> element
                        for search_elem in search_elements:
                            time_elem = search_elem.find('time')
                            if time_elem:
                                # Prefer datetime attribute (ISO format like "2026-02-17T05:34:00Z")
                                datetime_attr = time_elem.get('datetime')
                                if datetime_attr:
                                    time_text = datetime_attr
                                    print(f"  ⏰ Found time at level {search_elements.index(search_elem)}: {datetime_attr}")
                                    break
                                else:
                                    # Fall back to text content (like "2 days ago")
                                    text = time_elem.get_text(strip=True)
                                    if text:
                                        time_text = text
                                        print(f"  ⏰ Found time text at level {search_elements.index(search_elem)}: {text}")
                                        break
                        
                        # If still not found, do a broader search in the parent container
                        if not time_text and parent.parent:
                            all_times = parent.parent.find_all('time')
                            if all_times:
                                print(f"  🔍 Found {len(all_times)} <time> elements in broader search")
                                for t in all_times:
                                    dt = t.get('datetime')
                                    if dt:
                                        time_text = dt
                                        print(f"  ⏰ Using datetime: {dt}")
                                        break
                                    txt = t.get_text(strip=True)
                                    if txt and not time_text:
                                        time_text = txt
                                        print(f"  ⏰ Using text: {txt}")
                        
                        # Look for source in the same parent or nearby
                        for search_elem in [parent, parent.parent] if parent.parent else [parent]:
                            if source:
                                break
                            for elem in search_elem.find_all(['span', 'div', 'a'], recursive=False):
                                text = elem.get_text(strip=True)
                                # Source is usually a publication name
                                if not source and text and len(text) < 50 and len(text) > 2:
                                    # Common publication name patterns
                                    if any(word in text for word in ['Times', 'Post', 'News', 'Journal', 'Daily', 
                                                                      'Business', 'Financial', 'Economic', 'Wire',
                                                                      'Reuters', 'Bloomberg', 'CNN', 'BBC', 'CNBC',
                                                                      'Forbes', 'WSJ', 'Guardian', 'Today', 'Wire',
                                                                      'Herald', 'Tribune', 'Gazette']):
                                        source = text
                                        break
                    
                    # Build full URL
                    if href.startswith('./'):
                        full_url = urljoin(url, href.replace('./', '/'))
                    elif href.startswith('/'):
                        full_url = urljoin(url, href)
                    else:
                        full_url = href
                    
                    # Show warning if no time found
                    if not time_text:
                        print(f"  ⚠️  No timestamp found for this article")
                    
                    article_data = {
                        'title': title,
                        'url': full_url,
                        'source': source or 'Google News',
                        'published_at': time_text if time_text else 'Recently',
                        'crawled_at': datetime.utcnow().isoformat()
                    }
                    
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
                    
                    print(f"\n  📰 Processing article element: {title[:60]}...")
                    
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
                    
                    # If no source found, try other patterns
                    if not source:
                        for elem in article.find_all(['span', 'div']):
                            text = elem.get_text(strip=True)
                            if text and len(text) < 50 and any(word in text for word in ['Times', 'Post', 'News', 'Journal', 'Daily', 
                                                                  'Business', 'Financial', 'Economic', 'Wire',
                                                                  'Reuters', 'Bloomberg', 'CNN', 'BBC', 'CNBC',
                                                                  'Forbes', 'WSJ', 'Guardian', 'Today']):
                                source = text
                                break
                    
                    # Find time - Google News uses <time> tag with datetime attribute
                    # Structure: <time class="hvbAAd" datetime="2026-02-17T05:34:00Z">2 days ago</time>
                    time_text = None
                    
                    # Search all <time> elements in the article container
                    all_times = article.find_all('time')
                    if all_times:
                        print(f"  🔍 Found {len(all_times)} <time> elements in article")
                        for time_elem in all_times:
                            # Prefer datetime attribute (ISO format like "2026-02-17T05:34:00Z")
                            datetime_attr = time_elem.get('datetime')
                            if datetime_attr:
                                time_text = datetime_attr
                                print(f"  ⏰ Using datetime: {datetime_attr}")
                                break
                            # Fall back to text content (like "2 days ago")
                            text = time_elem.get_text(strip=True)
                            if text:
                                time_text = text
                                print(f"  ⏰ Using text: {text}")
                                break
                    
                    # Show warning if no time found
                    if not time_text:
                        print(f"  ⚠️  No timestamp found for this article")
                    
                    article_data = {
                        'title': title,
                        'url': full_url,
                        'source': source or 'Google News',
                        'published_at': time_text if time_text else 'Recently',
                        'crawled_at': datetime.utcnow().isoformat()
                    }
                    
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

