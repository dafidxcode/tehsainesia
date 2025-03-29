# Science and Technology News Aggregator and Blogger

This project automatically fetches the latest science and technology news from various countries, rewrites the content using AI in English to make it SEO-friendly, and posts it to a Blogger blog with images. The bot runs every 4 hours and avoids duplicating articles.

## Features

- Fetches science and technology news from multiple countries
- Rewrites content using OpenAI to make it human-like and SEO-optimized
- Finds relevant images for each article
- Posts to Blogger using the Blogger API
- Prevents duplicate articles
- Runs automatically every 4 hours
- Includes error handling and logging

## Requirements

- Python 3.7+
- Google API credentials for Blogger
- OpenAI API key
- NewsAPI key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/science-tech-news-bot.git
cd science-tech-news-bot
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your-openai-api-key
NEWS_API_KEY=your-newsapi-key
BLOGGER_CLIENT_ID=your-blogger-client-id
BLOGGER_CLIENT_SECRET=your-blogger-client-secret
BLOG_ID=your-blog-id
```

4. Run the setup script to authenticate with Google:
```bash
python setup.py
```

## Usage

### Running Manually

To run the bot manually:

```bash
python news_aggregator.py
```

### Running as a Service

#### On Linux with systemd

1. Edit the `science_tech_news_bot.service` file to update the paths and username.

2. Copy the service file to systemd:
```bash
sudo cp science_tech_news_bot.service /etc/systemd/system/
```

3. Enable and start the service:
```bash
sudo systemctl enable science_tech_news_bot.service
sudo systemctl start science_tech_news_bot.service
```

4. Check the status:
```bash
sudo systemctl status science_tech_news_bot.service
```

#### On Windows

1. Create a batch file `start_bot.bat`:
```batch
@echo off
python run_as_service.py
```

2. Create a shortcut to this batch file in the Windows Startup folder.

## Configuration

You can modify the following parameters in the `news_aggregator.py` file:

- `COUNTRIES`: List of country codes to fetch news from
- Scheduling interval (default is 4 hours)
- Number of articles to post per cycle (default is 3)

## Logging

Logs are stored in:
- `news_bot.log` - Main application logs
- `service_monitor.log` - Service monitor logs

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Make sure your Google API credentials are correct and have the necessary permissions.

2. **Rate Limiting**: If you encounter rate limiting from NewsAPI or OpenAI, try reducing the number of articles processed per cycle.

3. **Token Expiration**: If your Google token expires, delete the `token.pickle` file and run the setup script again.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

## 9. Let's create a simple script to check the status of the bot

```python:check_status.py
import os
import pickle
import logging
from datetime import datetime, timedelta

def check_bot_status():
    """Check the status of the news bot."""
    print("Science and Technology News Bot Status Check")
    print("===========================================")
    
    # Check log file
    if os.path.exists("news_bot.log"):
        with open("news_bot.log", "r") as f:
            log_lines = f.readlines()
            
        if log_lines:
            last_log = log_lines[-1]
            print(f"Last log entry: {last_log.strip()}")
            
            # Parse the timestamp from the log
            try:
                log_time_str = last_log.split(" - ")[0]
                log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S,%f")
                time_diff = datetime.now() - log_time
                
                print(f"Time since last activity: {time_diff}")
                
                if time_diff > timedelta(hours=5):
                    print("WARNING: Bot may be inactive. Last activity was more than 5 hours ago.")
                else:
                    print("Bot appears to be active.")
            except Exception as e:
                print(f"Could not parse log timestamp: {e}")
    else:
        print("No log file found. Bot may not have run yet.")
    
    # Check processed articles
    if os.path.exists("processed_articles.pkl"):
        with open("processed_articles.pkl", "rb") as f:
            processed_articles = pickle.load(f)
        
        print(f"Number of processed articles: {len(processed_articles)}")
    else:
        print("No processed articles file found.")
    
    print("\nTo restart the bot, run: python run_as_service.py")

if __name__ == "__main__":
    check_bot_status()
```

## 10. Let's create a script to test the OpenAI and NewsAPI connections

```python:test_connections.py
import os
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connections():
    """Test connections to required APIs."""
    print("Testing API Connections")
    print("======================")
    
    # Test OpenAI API
    print("\nTesting OpenAI API connection...")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=10
        )
        print("✅ OpenAI API connection successful!")
        print(f"Response: {response.choices[0].message['content']}")
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
    
    # Test NewsAPI
    print("\nTesting NewsAPI connection...")
    news_api_key = os.getenv("NEWS_API_KEY")
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&category=technology&apiKey={news_api_key}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') == 'ok':
            print("✅ NewsAPI connection successful!")
            print(f"Articles retrieved: {len(data.get('articles', []))}")
        else:
            print(f"❌ NewsAPI connection failed: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ NewsAPI connection failed: {str(e)}")
    
    # Test Blogger API credentials existence
    print("\nChecking Blogger API credentials...")
    if os.path.exists("blogger_credentials.json") and os.path.exists("token.pickle"):
        print("✅ Blogger API credentials found!")
    else:
        print("❌ Blogger API credentials not found. Run setup.py first.")

if __name__ == "__main__":
    test_connections()
    