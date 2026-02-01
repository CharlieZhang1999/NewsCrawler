# Semiconductor News Daily Summary

This repository contains a GitHub Actions workflow that automatically crawls semiconductor news from CNBC and sends you a beautiful HTML email with all the latest articles.

## How It Works

The workflow runs daily at **8am EST** and:
1. Fetches ALL latest articles from [CNBC Semiconductors](https://www.cnbc.com/semiconductors/)
2. Saves articles as JSON in `data/semiconductor_news.json`
3. Generates a beautiful HTML email with:
   - All articles with clickable titles
   - Timestamps for each article
   - Statistics (total articles, new articles today)
   - Professional newsletter-style formatting
4. Sends the email to `qiuyangzhangcharlie@gmail.com`
5. Commits the JSON data to GitHub

## Setup Instructions

### 1. Setup Gmail for Sending Emails

Follow the detailed guide: **[GMAIL_SETUP.md](GMAIL_SETUP.md)**

Quick summary:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate a Gmail App Password
3. Add two secrets to GitHub repository:
   - `GMAIL_SENDER`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: The 16-character app password

### 2. Configure GitHub Permissions

1. Go to repository **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

## Email Format

You'll receive a beautiful HTML email that includes:

- 📊 **Statistics Dashboard** - Total articles and new articles count
- 📰 **All Articles Listed** - Every article with title, link, and timestamp
- 🆕 **"NEW TODAY" Badges** - Highlights articles found in the current run
- 🎨 **Professional Design** - Modern, responsive HTML layout
- 📱 **Mobile-Friendly** - Looks great on phones, tablets, and desktop

The email will be sent to: **qiuyangzhangcharlie@gmail.com**

## Manual Trigger

You can manually trigger the workflow anytime:
1. Go to the **Actions** tab
2. Select **Daily Semiconductor News Summary** workflow
3. Click **Run workflow**
4. Click the green **Run workflow** button
5. Check your email inbox!

## Schedule

The workflow runs at **8am EST** (13:00 UTC):
- During **EST** (winter): 8am EST
- During **EDT** (summer): 9am EDT

To adjust timing, modify the cron expression in `.github/workflows/crawl_semiconductor_news.yml`:
- For 8am EDT: `"0 12 * * *"` (12:00 UTC)
- For 8am EST: `"0 13 * * *"` (13:00 UTC)

## Cost Considerations

**Free!** ✨ This setup is completely free:
- GitHub Actions: Free for public repositories
- Gmail SMTP: Free for personal use
- Web scraping: No API costs

## Troubleshooting

### Email not received
- Check spam/junk folder
- Verify Gmail secrets are set correctly (see GMAIL_SETUP.md)
- Check GitHub Actions logs for error messages

### Workflow fails
- Ensure GitHub Actions has write permissions
- Check that all secrets are added correctly
- Look at the Actions tab logs for specific errors

### No articles found
- CNBC may have changed their HTML structure
- Check if the website is accessible
- Look at the logs to see what was scraped

## Local Testing

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set Gmail credentials
export GMAIL_SENDER="youremail@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-app-password"

# Run the crawler
python scripts/crawl_semiconductor_news.py

# Send test email
python scripts/send_email.py
```

The data will be saved to `data/semiconductor_news.json` and an email will be sent.

## Files Structure

```
.
├── .github/workflows/
│   └── crawl_semiconductor_news.yml  # GitHub Actions workflow
├── scripts/
│   ├── crawl_semiconductor_news.py    # Web scraper for CNBC
│   └── send_email.py                  # HTML email sender
├── data/
│   └── semiconductor_news.json        # Crawled articles (JSON)
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
└── GMAIL_SETUP.md                     # Gmail setup guide
```
