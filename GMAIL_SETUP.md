# Gmail Setup Guide for Email Notifications

Follow these steps to enable Gmail to send your daily semiconductor news emails.

## Step 1: Enable 2-Factor Authentication on Gmail

Gmail App Passwords require 2-Factor Authentication to be enabled.

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification if not already enabled

## Step 2: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
4. Scroll down to the bottom and click **App passwords**
   - If you don't see this option, make sure 2-Step Verification is fully enabled
5. You may need to sign in again
6. Under "Select app", choose **Mail**
7. Under "Select device", choose **Other (Custom name)**
8. Type a name like "GitHub Actions - Semiconductor News"
9. Click **Generate**
10. **Copy the 16-character password** that appears (it will look like: `xxxx xxxx xxxx xxxx`)
    - ⚠️ **Important:** You won't be able to see this password again!

## Step 3: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Add First Secret:
- **Name:** `GMAIL_SENDER`
- **Value:** Your Gmail address (e.g., `youremail@gmail.com`)
- Click **Add secret**

### Add Second Secret:
- Click **New repository secret** again
- **Name:** `GMAIL_APP_PASSWORD`
- **Value:** The 16-character app password you generated (paste without spaces)
- Click **Add secret**

## Step 4: Verify Setup

You should now have these secrets in your repository:
- ✅ `GMAIL_SENDER`
- ✅ `GMAIL_APP_PASSWORD`

## Step 5: Test the Email

### Option A: Manual Test
Run the workflow manually to test:
1. Go to **Actions** tab in your repository
2. Click **Daily Semiconductor News Summary**
3. Click **Run workflow**
4. Wait for it to complete
5. Check your inbox at `qiuyangzhangcharlie@gmail.com`

### Option B: Local Test
Test locally before pushing:

```bash
# Set environment variables
export GMAIL_SENDER="youremail@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-password"

# Run the scripts
cd "Semiconductor Workflow"
python scripts/crawl_semiconductor_news.py
python scripts/send_email.py
```

## Troubleshooting

### "Authentication failed" error
- Make sure you're using the **App Password**, not your regular Gmail password
- Double-check the App Password was copied correctly (remove any spaces)
- Verify 2-Step Verification is enabled

### "GMAIL_SENDER and GMAIL_APP_PASSWORD must be set" error
- Make sure you added both secrets to GitHub
- Secret names must match exactly (case-sensitive)

### Email not received
- Check your spam/junk folder
- Verify the recipient email is correct in `scripts/send_email.py`
- Check GitHub Actions logs for error messages

### "Less secure app access" message
- This is outdated - use App Passwords instead
- App Passwords are the secure method for 2FA-enabled accounts

## Security Notes

- ✅ **App Passwords are secure** - They're app-specific and can be revoked
- ✅ **GitHub Secrets are encrypted** - They're not visible in logs or to other users
- 🔒 **Never commit passwords** - Always use environment variables/secrets
- 🗑️ **Revoke if compromised** - You can delete app passwords anytime in Google Account settings

## Email Features

Your daily email will include:
- 📊 **Statistics** - Total articles and new articles today
- 📰 **All articles** with clickable titles
- 🕐 **Timestamps** for each article
- 🎨 **Beautiful HTML formatting** - Professional newsletter style
- 📱 **Mobile-responsive** - Looks great on all devices
- 🆕 **"NEW TODAY" badges** - Highlights the latest articles

## Next Steps

Once setup is complete:
- The workflow runs automatically at 8am EST daily
- You'll receive an email at `qiuyangzhangcharlie@gmail.com`
- The email will contain ALL articles found, not just 3
- Articles are sorted from newest to oldest

