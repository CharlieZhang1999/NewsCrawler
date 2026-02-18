# Google News Crawler - Important Notes

## Overview

I've created a separate crawler for Google News (`scripts/crawl_google_news.py`) because it has a completely different HTML structure from CNBC.

## Challenges with Google News Scraping

### 1. **JavaScript-Heavy Content**
Google News is heavily JavaScript-rendered, meaning:
- Much of the content loads dynamically after the page loads
- Simple HTTP requests may not capture all articles
- The current crawler uses `requests` + `BeautifulSoup`, which only gets static HTML

### 2. **Dynamic CSS Classes**
- Google News uses randomized or frequently-changing CSS class names
- This makes it hard to write stable selectors
- The structure can change without notice

### 3. **Anti-Scraping Measures**
- Google has rate limiting
- May detect and block automated scrapers
- CAPTCHA challenges may appear

### 4. **Redirect URLs**
- Article URLs often use Google's redirect format: `./articles/...`
- These need special handling to extract actual article URLs

## Current Implementation

The crawler (`scripts/crawl_google_news.py`) attempts to:
1. Find `<article>` elements
2. Extract links containing `/articles/`
3. Parse titles, sources, and timestamps from nearby elements
4. Save to `data/google_news_semiconductor.json`

**Note:** This may not capture all articles due to JavaScript rendering.

## Recommended Solution: Selenium

For better results with Google News, consider using Selenium or Playwright:

### Install Selenium:
```bash
pip install selenium webdriver-manager
```

### Updated Crawler Example:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_google_news_with_selenium():
    options = Options()
    options.add_argument('--headless')  # Run without opening browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    url = "https://news.google.com/topics/semiconductor"
    driver.get(url)
    
    # Wait for content to load
    time.sleep(3)
    
    # Now you can access the fully rendered page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extract articles...
    
    driver.quit()
```

## Alternative: Google News RSS Feed

Google News provides RSS feeds which are more reliable:

```python
import feedparser

# Google News RSS for semiconductor news
rss_url = "https://news.google.com/rss/search?q=semiconductor&hl=en-US&gl=US&ceid=US:en"

feed = feedparser.parse(rss_url)

for entry in feed.entries:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Published: {entry.published}")
```

This is **much more reliable** than web scraping!

## Current Setup

The workflow now runs both crawlers:
1. `crawl_semiconductor_news.py` - CNBC (works reliably)
2. `crawl_google_news.py` - Google News (may have limited results)
3. `crawl_all_sources.py` - Combines both sources

The combined data is saved to `data/combined_semiconductor_news.json` and used for email.

## If Google News Crawler Isn't Working

If you find the Google News crawler isn't capturing articles:

### Quick Fix: Use RSS Feed Instead
Edit `scripts/crawl_google_news.py` to use RSS feed (more reliable).

### Better Fix: Add Selenium
Update `requirements.txt`:
```
selenium>=4.15.0
webdriver-manager>=4.0.0
```

Then modify the crawler to use Selenium as shown above.

## Testing

Test the Google News crawler locally:

```bash
# Test Google News crawler
python scripts/crawl_google_news.py

# Test all crawlers combined
python scripts/crawl_all_sources.py
```

Check the output to see how many articles were captured.

## Recommendation

For production use, I recommend:
1. **Use RSS feeds** for Google News (most reliable)
2. Keep CNBC web scraping (works well with BeautifulSoup)
3. Combine both sources for comprehensive coverage

Would you like me to implement the RSS feed approach? It's more reliable and won't break as easily!

