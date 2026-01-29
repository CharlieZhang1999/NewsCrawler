# Semiconductor News Daily Summary - AI-Powered

This repository contains a GitHub Actions workflow that automatically generates AI-powered daily summaries of semiconductor news from CNBC.

## How It Works

The workflow runs daily at **8am EST** and:
1. Fetches the latest articles from [CNBC Semiconductors](https://www.cnbc.com/semiconductors/)
2. Uses AI (OpenAI GPT-4 or Anthropic Claude) to analyze and summarize the news
3. Generates a comprehensive markdown summary with:
   - Links to all news articles
   - Key tech trends (2-3 major themes)
   - Major announcements
   - Industry impact analysis
4. Commits the summary to the `summaries/` folder
5. Pushes to GitHub (which triggers email notifications if enabled)

## Setup Instructions

### 1. Get an AI API Key

You need an API key from either:

#### Option A: OpenAI (Recommended)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (starts with `sk-...`)

#### Option B: Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key

### 2. Add API Key to GitHub Secrets

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add one of these secrets:
   - For OpenAI: Name: `OPENAI_API_KEY`, Value: your API key
   - For Claude: Name: `ANTHROPIC_API_KEY`, Value: your API key

### 3. Configure GitHub Permissions

1. Go to repository **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

### 4. (Optional) Switch to Claude

If you want to use Anthropic Claude instead of OpenAI:

1. Open `.github/workflows/crawl_semiconductor_news.yml`
2. In the `env:` section, uncomment these lines:
   ```yaml
   ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
   AI_API_TYPE: anthropic
   ```
3. Comment out the OpenAI lines

## Email Notifications

To receive email notifications when summaries are generated:

### Option A: GitHub Email Notifications
1. Go to your GitHub **Settings** → **Notifications**
2. Enable email notifications for **Commits**
3. Make sure you're watching this repository (Watch → All Activity)

### Option B: Watch the Repository
1. Click **Watch** at the top of the repository
2. Select **All Activity**
3. You'll get emails for every commit

## Manual Trigger

You can manually generate a summary anytime:
1. Go to the **Actions** tab
2. Select **Daily Semiconductor News Summary** workflow
3. Click **Run workflow**
4. Click the green **Run workflow** button

## Summary Format

Each daily summary includes:

```markdown
# Semiconductor News Summary - YYYY-MM-DD

## LINKS TO THE NEWS
- List of all articles with titles and links

## KEY TECH TRENDS
- 2-3 major themes identified from the news

## MAJOR ANNOUNCEMENTS
- Significant product launches, acquisitions, company news

## INDUSTRY IMPACT
- Analysis of how these developments affect the tech ecosystem

## All Articles
- Complete list of all articles found
```

Summaries are saved in the `summaries/` folder with filenames like:
- `semiconductor_news_2026-01-29.md`
- `semiconductor_news_2026-01-30.md`

## Schedule

The workflow runs at **8am EST** (13:00 UTC):
- During **EST** (winter): 8am EST
- During **EDT** (summer): 9am EDT

To adjust timing, modify the cron expression in `.github/workflows/crawl_semiconductor_news.yml`:
- For 8am EDT: `"0 12 * * *"` (12:00 UTC)
- For 8am EST: `"0 13 * * *"` (13:00 UTC)

## Cost Considerations

### OpenAI API Costs
- GPT-4: ~$0.01-0.03 per summary (based on ~500-1000 tokens)
- GPT-3.5-Turbo: ~$0.001 per summary (cheaper alternative)

To use GPT-3.5-Turbo instead, edit `scripts/generate_daily_summary.py`:
```python
model="gpt-3.5-turbo"  # instead of "gpt-4"
```

### Anthropic API Costs
- Claude 3.5 Sonnet: ~$0.015 per summary

Monthly cost estimate: **$0.30-$0.90** (assuming daily runs)

## Troubleshooting

### Workflow fails with "No API key found"
- Make sure you've added `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to GitHub Secrets
- Check that the secret name matches exactly (case-sensitive)

### No commit/push happens
- Check that GitHub Actions has write permissions (see Setup step 3)
- Look at the workflow logs in the Actions tab for error messages

### Summary quality issues
- GPT-4 generally provides better analysis than GPT-3.5-Turbo
- Claude 3.5 Sonnet is comparable to GPT-4
- You can adjust the prompt in `scripts/generate_daily_summary.py`

## Local Testing

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY="your-key-here"
# OR
export ANTHROPIC_API_KEY="your-key-here"
export AI_API_TYPE="anthropic"

# Run the script
python scripts/generate_daily_summary.py
```

The summary will be saved to `summaries/semiconductor_news_YYYY-MM-DD.md`

## Files Structure

```
.
├── .github/workflows/
│   └── crawl_semiconductor_news.yml  # GitHub Actions workflow
├── scripts/
│   ├── generate_daily_summary.py      # Main AI summary generator
│   └── crawl_semiconductor_news.py    # (old scraper, kept for reference)
├── summaries/                          # Generated summaries stored here
│   └── semiconductor_news_*.md
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```
