# Semiconductor News Crawler - GitHub Actions Workflow

This repository contains a GitHub Actions workflow that automatically crawls semiconductor news and commits the results.

## Workflow Overview

The workflow (`/.github/workflows/crawl_semiconductor_news.yml`) runs daily at **8am EST** (13:00 UTC) and:
1. Runs the crawler script at `scripts/crawl_semiconductor_news.py`
2. Commits any changes to the repository
3. Pushes the commit to trigger notifications

## Setup Instructions

### 1. Place Your Crawler Script
Ensure your crawler script exists at:
```
scripts/crawl_semiconductor_news.py
```

### 2. Dependencies
If your script requires Python packages, create a `requirements.txt` file in the root directory. The workflow will automatically install dependencies if this file exists.

### 3. GitHub Permissions
The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions. For the workflow to push commits, you may need to:

1. Go to your repository **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

### 4. Email Notifications

GitHub Actions doesn't send emails directly. To receive email notifications when commits are made, you have several options:

#### Option A: GitHub Email Notifications (Recommended)
1. Go to your GitHub **Settings** → **Notifications**
2. Enable email notifications for:
   - **Commits** (when commits are made to repositories you watch)
   - **Actions** (when workflows run)

#### Option B: Add Email Service to Workflow
You can add an email step to the workflow using a service like SendGrid, Mailgun, or SMTP. Example:

```yaml
- name: Send email notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "Semiconductor News Update"
    to: your-email@example.com
    from: GitHub Actions
    body: "The semiconductor news crawler has completed and committed new data."
```

Then add your email credentials as GitHub Secrets.

## Manual Trigger

You can manually trigger the workflow by:
1. Going to the **Actions** tab in your repository
2. Selecting **Crawl Semiconductor News** workflow
3. Clicking **Run workflow**

## Cron Schedule

The workflow runs at **8am EST** (13:00 UTC). Note:
- During **EST** (winter): Runs at 8am EST
- During **EDT** (summer): Runs at 9am EDT

To adjust for daylight saving time, modify the cron expression in the workflow file:
- For 8am EDT: `"0 12 * * *"` (12:00 UTC)
- For 8am EST: `"0 13 * * *"` (13:00 UTC)

