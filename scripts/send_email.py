#!/usr/bin/env python3
"""
Send HTML email with semiconductor news articles.
Uses Gmail SMTP to send beautifully formatted HTML emails.
"""

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def load_articles(json_file='data/semiconductor_news.json'):
    """
    Load articles from JSON file.
    """
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None


def generate_html_email(data):
    """
    Generate detailed HTML email with all articles.
    """
    if not data or 'articles' not in data:
        return None
    
    articles = data['articles']
    total_articles = data.get('total_articles', len(articles))
    new_articles = data.get('new_articles_today', 0)
    last_updated = data.get('last_updated', '')
    
    # Parse timestamp
    try:
        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        formatted_date = dt.strftime('%B %d, %Y at %I:%M %p UTC')
    except:
        formatted_date = last_updated
    
    # Start HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semiconductor News Update</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .stats {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }}
        .stat {{
            text-align: center;
            padding: 10px;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .content {{
            padding: 30px;
        }}
        .article {{
            padding: 20px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-number {{
            display: inline-block;
            background-color: #667eea;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            text-align: center;
            line-height: 32px;
            font-weight: bold;
            font-size: 14px;
            margin-right: 12px;
            vertical-align: middle;
        }}
        .article-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin: 0 0 8px 0;
            line-height: 1.4;
        }}
        .article-title a {{
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.2s;
        }}
        .article-title a:hover {{
            color: #667eea;
        }}
        .article-meta {{
            font-size: 13px;
            color: #6c757d;
            margin: 8px 0 0 44px;
        }}
        .article-meta span {{
            margin-right: 15px;
        }}
        .time-icon {{
            color: #667eea;
        }}
        .link-icon {{
            color: #28a745;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 44px;
            margin-top: 8px;
        }}
        .badge-new {{
            background-color: #d4edda;
            color: #155724;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .divider {{
            border: 0;
            height: 1px;
            background: linear-gradient(to right, transparent, #667eea, transparent);
            margin: 30px 0;
        }}
        @media only screen and (max-width: 600px) {{
            .stats {{
                flex-direction: column;
            }}
            .article-title {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Daily Semiconductor News</h1>
            <p>Your comprehensive update from CNBC</p>
            <p>{formatted_date}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat">
                <div class="stat-number">{new_articles}</div>
                <div class="stat-label">New Today</div>
            </div>
        </div>
        
        <div class="content">
            <h2 style="margin-top: 0; color: #2c3e50;">Latest Articles</h2>
"""
    
    # Add each article
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        url = article.get('url', '#')
        time = article.get('published_time', '')
        source = article.get('source', 'CNBC')
        
        # Determine if this is a new article (among today's new articles)
        is_new = i <= new_articles
        
        html += f"""
            <div class="article">
                <div>
                    <span class="article-number">{i}</span>
                    <h3 class="article-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </h3>
                </div>
                <div class="article-meta">
"""
        
        if time:
            html += f'<span><span class="time-icon">🕐</span> {time}</span>'
        
        html += f"""
                    <span><span class="link-icon">🔗</span> {source}</span>
                </div>
"""
        
        if is_new:
            html += '<div><span class="badge badge-new">NEW TODAY</span></div>'
        
        html += """
            </div>
"""
    
    # Close HTML
    html += f"""
        </div>
        
        <div class="footer">
            <p><strong>Source:</strong> <a href="https://www.cnbc.com/semiconductors/" target="_blank">CNBC Semiconductors</a></p>
            <p>Automated by GitHub Actions • Generated at {formatted_date}</p>
            <p style="margin-top: 15px; font-size: 11px; color: #adb5bd;">
                You're receiving this because you subscribed to daily semiconductor news updates.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def send_email(to_email, subject, html_content):
    """
    Send HTML email via Gmail SMTP.
    """
    # Get credentials from environment variables
    sender_email = os.environ.get('GMAIL_SENDER')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not sender_email or not sender_password:
        print("Error: GMAIL_SENDER and GMAIL_APP_PASSWORD environment variables must be set")
        return False
    
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = to_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Connect to Gmail SMTP server
        print(f"Connecting to Gmail SMTP server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        
        # Send email
        print(f"Sending email to {to_email}...")
        server.sendmail(sender_email, to_email, message.as_string())
        server.quit()
        
        print("✓ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Semiconductor News Email Sender")
    print("=" * 60)
    
    # Recipient email
    recipient = "qiuyangzhangcharlie@gmail.com"
    
    # Load articles
    print("\nLoading articles from JSON...")
    data = load_articles()
    
    if not data:
        print("No data to send")
        return
    
    # Generate HTML
    print("Generating HTML email...")
    html = generate_html_email(data)
    
    if not html:
        print("Failed to generate HTML")
        return
    
    # Create subject line
    new_count = data.get('new_articles_today', 0)
    total_count = data.get('total_articles', 0)
    today = datetime.utcnow().strftime('%b %d, %Y')
    subject = f"📰 Daily Semiconductor News - {new_count} New Articles ({today})"
    
    # Send email
    success = send_email(recipient, subject, html)
    
    if success:
        print(f"\n✓ Successfully sent email to {recipient}")
    else:
        print(f"\n✗ Failed to send email")


if __name__ == "__main__":
    main()
