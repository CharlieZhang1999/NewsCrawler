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
    
    # CNBC URLs - separated by filtering needs
    # Semiconductor-specific URLs: collect ALL articles (no filtering)
    semiconductor_urls = [
        "https://www.cnbc.com/semiconductors/",
    ]
    
    # General URLs: filter by keywords
    general_urls = [
        "https://www.cnbc.com/technology/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    found_links = set()
    
    # Process semiconductor URLs (no filtering)
    for url in semiconductor_urls:
        try:
            print(f"Fetching semiconductor section: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all Card-titleContainer elements (each contains an article)
            card_containers = soup.find_all(class_='Card-titleContainer')
            
            for container in card_containers:
                try:
                    # Find the link with class "Card-title" inside the container
                    link_elem = container.find('a', class_='Card-title')
                    
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        full_url = urljoin(url, href)

                        # Only keep CNBC links
                        parsed_full = urlparse(full_url)
                        if parsed_full.netloc and "cnbc.com" not in parsed_full.netloc:
                            continue
                        
                        # Skip if we've already seen this URL
                        if full_url in found_links:
                            continue
                        
                        # Extract title (prefer the link text; fallback to container text)
                        title = link_elem.get_text(strip=True) or container.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue
                        
                        # Extract time from Card-time
                        time_elem = container.find(class_='Card-time')
                        if not time_elem:
                            parent = container.parent
                            if parent:
                                time_elem = parent.find(class_='Card-time')
                                if not time_elem and parent.parent:
                                    time_elem = parent.parent.find(class_='Card-time')
                        
                        time_text = time_elem.get_text(strip=True) if time_elem else None
                        
                        # No filtering - keep all articles from semiconductor section
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
    
    # Process general URLs (with keyword filtering)
    for url in general_urls:
        try:
            print(f"Fetching general section: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all Card-titleContainer elements (each contains an article)
            card_containers = soup.find_all(class_='Card-titleContainer')
            
            for container in card_containers:
                try:
                    # Find the link with class "Card-title" inside the container
                    link_elem = container.find('a', class_='Card-title')
                    
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        full_url = urljoin(url, href)

                        # Only keep CNBC links
                        parsed_full = urlparse(full_url)
                        if parsed_full.netloc and "cnbc.com" not in parsed_full.netloc:
                            continue
                        
                        # Skip if we've already seen this URL
                        if full_url in found_links:
                            continue
                        
                        # Extract title (prefer the link text; fallback to container text)
                        title = link_elem.get_text(strip=True) or container.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue
                        
                        # Extract time from Card-time
                        time_elem = container.find(class_='Card-time')
                        if not time_elem:
                            parent = container.parent
                            if parent:
                                time_elem = parent.find(class_='Card-time')
                                if not time_elem and parent.parent:
                                    time_elem = parent.parent.find(class_='Card-time')
                        
                        time_text = time_elem.get_text(strip=True) if time_elem else None
                        
                        # Filter by keywords for general sections
                        container_text = container.get_text().lower()
                        title_lower = title.lower() if title else ''
                        url_lower = full_url.lower()
                        
                        keywords = ['semiconductor', 'chip', 'technology', 'tech', 'nvidia', 'amd', 'intel', 'tsmc']
                        should_keep = any(
                            (keyword in url_lower) or (keyword in title_lower) or (keyword in container_text)
                            for keyword in keywords
                        )
                        
                        if should_keep:
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
    
    # Add new articles that don't already exist
    all_articles = [article for article in articles]
    
    
    # Save to file
    output_data = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_articles': len(all_articles),
        'articles_today': len(all_articles),
        'articles': all_articles
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(all_articles)} new articles. Total articles: {len(all_articles)}")
    return len(all_articles)


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

