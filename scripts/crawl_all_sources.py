    #!/usr/bin/env python3
"""
Master crawler that runs all news sources and combines results.
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def run_crawler(script_name):
    """
    Run a crawler script and return success status.
    """
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {script_name} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Error running {script_name}: {e}")
        return False


def combine_data_sources():
    """
    Combine data from all sources into a master file.
    """
    print(f"\n{'='*60}")
    print("Combining data from all sources")
    print(f"{'='*60}\n")
    
    data_files = [
        'data/semiconductor_news.json',  # CNBC
        'data/google_news_semiconductor.json',  # Google News
    ]
    
    combined_articles = []
    stats = {}
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            print(f"  ⚠ Skipping {file_path} (not found)")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, dict) and 'articles' in data:
                articles = data['articles']
                source_name = data.get('source', file_path)
                stats[source_name] = {
                    'total': len(articles),
                    'new_today': data.get('new_articles_today', 0)
                }
                combined_articles.extend(articles)
                print(f"  ✓ {source_name}: {len(articles)} articles ({data.get('new_articles_today', 0)} new)")
            elif isinstance(data, list):
                combined_articles.extend(data)
                print(f"  ✓ {file_path}: {len(data)} articles")
                
        except Exception as e:
            print(f"  ✗ Error reading {file_path}: {e}")
    
    # Remove duplicates based on title (case-insensitive)
    seen_titles = set()
    unique_articles = []
    
    for article in combined_articles:
        title = article.get('title', '').lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    duplicates_removed = len(combined_articles) - len(unique_articles)
    
    # Save combined data
    combined_data = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_articles': len(unique_articles),
        'sources': stats,
        'duplicates_removed': duplicates_removed,
        'articles': unique_articles
    }
    
    output_file = 'data/combined_semiconductor_news.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("Combined Data Summary")
    print(f"{'='*60}")
    print(f"Total unique articles: {len(unique_articles)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Saved to: {output_file}\n")
    
    return output_file


def main():
    """Main function."""
    print("=" * 60)
    print("Master Semiconductor News Crawler")
    print("=" * 60)
    print(f"Time: {datetime.utcnow().isoformat()}\n")
    
    # List of crawler scripts to run
    crawlers = [
        'crawl_semiconductor_news.py',  # CNBC
        'crawl_google_news.py',         # Google News
    ]
    
    # Run all crawlers
    results = {}
    for crawler in crawlers:
        results[crawler] = run_crawler(crawler)
    
    # Combine all data sources
    combined_file = combine_data_sources()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Crawling Summary")
    print("=" * 60)
    
    for crawler, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"{status}: {crawler}")
    
    print(f"\nCombined data saved to: {combined_file}")
    print("\n✓ All crawlers completed!")


if __name__ == "__main__":
    main()

