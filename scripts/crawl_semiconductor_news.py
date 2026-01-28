#!/usr/bin/env python3
"""
CNBC Semiconductor News Crawler
Crawls CNBC for semiconductor-related news articles and saves them to a JSON file.
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse


def get_cnbc_semiconductor_news():
    """
    Crawl CNBC for semiconductor news articles.
    Returns a list of article dictionaries.
    """
    articles = []
    
    # CNBC semiconductor news URLs
    urls = [
        "https://www.cnbc.com/semiconductors/",
        "https://www.cnbc.com/technology/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in urls:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all Card-titleContainer elements (each contains an article)
            card_containers = soup.find_all(class_='Card-titleContainer')
            found_links = set()
            
            for container in card_containers:
                try:
                    # Find the link with class "Card-title" inside the container
                    link_elem = container.find('a', class_='Card-title')
                    
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        full_url = urljoin(url, href)
                        
                        # Skip if we've already seen this URL
                        if full_url in found_links:
                            continue
                        
                        # Extract title from Card-titleContainer
                        title = container.get_text(strip=True)
                        # If title is empty, try getting it from the link
                        if not title or len(title) < 10:
                            title = link_elem.get_text(strip=True)
                        
                        # Extract time from Card-time
                        # First try within the container itself
                        time_elem = container.find(class_='Card-time')
                        
                        # If not found, search in parent and nearby elements
                        if not time_elem:
                            parent = container.parent
                            if parent:
                                # Search in parent
                                time_elem = parent.find(class_='Card-time')
                                # If still not found, search in parent's siblings
                                if not time_elem and parent.parent:
                                    time_elem = parent.parent.find(class_='Card-time')
                        
                        time_text = time_elem.get_text(strip=True) if time_elem else None
                        
                        # Filter for semiconductor-related articles
                        # Check URL, title, or container text for keywords
                        container_text = container.get_text().lower()
                        title_lower = title.lower() if title else ''
                        url_lower = full_url.lower()
                        
                        if any(keyword in url_lower or keyword in title_lower or keyword in container_text 
                               for keyword in ['semiconductor', 'chip', 'technology', 'tech', 'nvidia', 'amd', 'intel', 'tsmc']):
                            found_links.add(full_url)
                            
                            article_data = {
                                'title': title,
                                'url': full_url,
                                'source': 'CNBC',
                                'crawled_at': datetime.utcnow().isoformat()
                            }
                            
                            if time_text:
                                article_data['published_time'] = time_text
                            
                            articles.append(article_data)
                            
                except Exception as e:
                    print(f"Error processing card container: {e}")
                    continue
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            continue
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    return unique_articles


def save_articles(articles, output_file='data/semiconductor_news.json'):
    """
    Save articles to a JSON file.
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Load existing articles if file exists
    existing_articles = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    existing_articles = existing_data
                elif isinstance(existing_data, dict) and 'articles' in existing_data:
                    existing_articles = existing_data['articles']
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Create a set of existing URLs to avoid duplicates
    existing_urls = {article.get('url', '') for article in existing_articles}
    
    # Add new articles that don't already exist
    new_articles = [article for article in articles if article.get('url', '') not in existing_urls]
    
    # Combine existing and new articles
    all_articles = existing_articles + new_articles
    
    # Save to file
    output_data = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_articles': len(all_articles),
        'new_articles_today': len(new_articles),
        'articles': all_articles
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(new_articles)} new articles. Total articles: {len(all_articles)}")
    return len(new_articles)


def main():
    """Main function to run the crawler."""
    print("Starting CNBC Semiconductor News Crawler...")
    print(f"Time: {datetime.utcnow().isoformat()}\n")
    
    articles = get_cnbc_semiconductor_news()
    
    if articles:
        print(f"\nFound {len(articles)} semiconductor-related articles")
        new_count = save_articles(articles)
        print(f"Crawler completed successfully. {new_count} new articles added.")
    else:
        print("No articles found. This might be due to:")
        print("1. Website structure changes")
        print("2. Network issues")
        print("3. No semiconductor news available at this time")
        # Still create/update the file to show the crawl was attempted
        save_articles([])


if __name__ == "__main__":
    main()

