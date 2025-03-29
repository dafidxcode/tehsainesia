import requests
import json
import os
import time
import hashlib
import random
import schedule
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import openai
from urllib.parse import urlparse
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_bot.log"),
        logging.StreamHandler()
    ]
)

# API Keys and Configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BLOGGER_CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
BLOGGER_CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
BLOG_ID = os.getenv("BLOG_ID")

# Set up OpenAI
openai.api_key = OPENAI_API_KEY

# File to store processed articles
PROCESSED_ARTICLES_FILE = "processed_articles.pkl"
CREDENTIALS_FILE = "blogger_credentials.json"
TOKEN_FILE = "token.pickle"

# Scopes for Google API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Countries to fetch news from
COUNTRIES = ['us', 'gb', 'au', 'ca', 'in', 'sg', 'jp']

def get_blogger_service():
    """Set up and return the Blogger API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('blogger', 'v3', credentials=creds)

def load_processed_articles():
    """Load the list of already processed articles."""
    if os.path.exists(PROCESSED_ARTICLES_FILE):
        with open(PROCESSED_ARTICLES_FILE, 'rb') as f:
            return pickle.load(f)
    return set()

def save_processed_articles(processed_articles):
    """Save the updated list of processed articles."""
    with open(PROCESSED_ARTICLES_FILE, 'wb') as f:
        pickle.dump(processed_articles, f)

def fetch_science_tech_news():
    """Fetch science and technology news from various countries."""
    all_articles = []
    
    for country in COUNTRIES:
        try:
            # Science news
            science_url = f"https://newsapi.org/v2/top-headlines?country={country}&category=science&apiKey={NEWS_API_KEY}"
            science_response = requests.get(science_url)
            science_data = science_response.json()
            
            # Technology news
            tech_url = f"https://newsapi.org/v2/top-headlines?country={country}&category=technology&apiKey={NEWS_API_KEY}"
            tech_response = requests.get(tech_url)
            tech_data = tech_response.json()
            
            if science_data.get('status') == 'ok':
                all_articles.extend(science_data.get('articles', []))
            
            if tech_data.get('status') == 'ok':
                all_articles.extend(tech_data.get('articles', []))
                
            # Avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"Error fetching news from {country}: {str(e)}")
    
    return all_articles

def get_article_hash(article):
    """Generate a unique hash for an article based on title and URL."""
    unique_string = f"{article['title']}{article['url']}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def rewrite_with_ai(article):
    """Rewrite the article using OpenAI to make it SEO-friendly and human-like."""
    try:
        # Extract content
        title = article['title']
        description = article.get('description', '')
        content = article.get('content', '')
        url = article['url']
        
        # Get more content from the original URL if available
        full_content = description + " " + content
        if len(full_content) < 200:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = soup.find_all('p')
                    additional_content = ' '.join([p.text for p in paragraphs[:5]])
                    full_content += " " + additional_content
            except Exception as e:
                logging.warning(f"Could not fetch additional content: {str(e)}")
        
        # Create prompt for OpenAI
        prompt = f"""
        Rewrite the following science/technology news article in a human-like, engaging style.
        Make it SEO-friendly with appropriate headings, subheadings, and keywords.
        Include an introduction, main content with 3-5 paragraphs, and a conclusion.
        
        Original Title: {title}
        Original Content: {full_content}
        Source URL: {url}
        
        Format the article with:
        1. An engaging H1 title (different from the original but capturing the essence)
        2. A compelling introduction
        3. H2 subheadings for main sections
        4. Bullet points where appropriate
        5. A conclusion paragraph
        6. Include relevant keywords naturally throughout the text
        7. Add meta description for SEO
        
        Return the article in HTML format ready for publishing.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert science and technology writer who creates engaging, SEO-optimized content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        rewritten_content = response.choices[0].message['content'].strip()
        
        # Extract a new title from the rewritten content
        soup = BeautifulSoup(rewritten_content, 'html.parser')
        h1_tag = soup.find('h1')
        new_title = h1_tag.text if h1_tag else title
        
        # Generate meta description for SEO
        meta_prompt = f"Generate a compelling meta description (under 160 characters) for this article about: {new_title}"
        meta_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an SEO expert."},
                {"role": "user", "content": meta_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        meta_description = meta_response.choices[0].message['content'].strip()
        
        return {
            'title': new_title,
            'content': rewritten_content,
            'original_url': url,
            'meta_description': meta_description
        }
        
    except Exception as e:
        logging.error(f"Error rewriting article: {str(e)}")
        return None

def get_image_from_article(article):
    """Extract image from the article or find a free-to-use image."""
    try:
        # First try to get the image from the article
        if article.get('urlToImage'):
            image_url = article['urlToImage']
            # Check if the image URL is valid
            response = requests.head(image_url)
            if response.status_code == 200:
                return image_url
        
        # If no image or invalid image, try to extract one from the article content
        url = article['url']
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img', src=True)
            
            for img in images:
                if img['src'].startswith('http') and not any(x in img['src'].lower() for x in ['icon', 'logo', 'avatar']):
                    # Check if the image is accessible
                    try:
                        img_response = requests.head(img['src'], timeout=5)
                        if img_response.status_code == 200:
                            return img['src']
                    except:
                        continue
        
        # If still no image, use a placeholder from Unsplash (free to use)
        keywords = '+'.join(article['title'].split()[:3])
        return f"https://source.unsplash.com/featured/?{keywords}"
        
    except Exception as e:
        logging.error(f"Error getting image: {str(e)}")
        # Return a generic science/tech image
        return "https://source.unsplash.com/featured/?science,technology"

def post_to_blogger(article, image_url):
    """Post the rewritten article to Blogger."""
    try:
        service = get_blogger_service()
        
        # Add image to the content with proper alt text for SEO
        image_html = f'<div class="post-image"><img src="{image_url}" alt="{article["title"]}" title="{article["title"]}" /></div>'
        
        # Add source attribution
        source_html = f'<p class="source">Source: <a href="{article["original_url"]}" target="_blank" rel="nofollow">Original Article</a></p>'
        
        # Prepare the post content
        content = f"{image_html}\n{article['content']}\n{source_html}"
        
        # Create post body with meta description for SEO
        post_body = {
            'kind': 'blogger#post',
            'title': article['title'],
            'content': content,
            'labels': ['Science', 'Technology', 'News', 'Innovation'],
            'author': {
                'displayName': 'Science & Tech News'
            }
        }
        
        # Post to Blogger
        post = service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
        
        # Update the post with custom meta description
        if article.get('meta_description'):
            post['content'] = f'<!-- meta-description: {article["meta_description"]} -->\n{post["content"]}'
            service.posts().update(blogId=BLOG_ID, postId=post['id'], body=post).execute()
            
        logging.info(f"Posted article: {article['title']} - Post ID: {post['id']}")
        return True
        
    except Exception as e:
        logging.error(f"Error posting to Blogger: {str(e)}")
        return False

def process_news():
    """Main function to process news articles."""
    logging.info("Starting news processing cycle")
    
    # Load already processed articles
    processed_articles = load_processed_articles()
    
    # Fetch news
    articles = fetch_science_tech_news()
    logging.info(f"Fetched {len(articles)} articles")
    
    # Process each article
    articles_posted = 0
    for article in articles:
        # Skip if no title or URL
        if not article.get('title') or not article.get('url'):
            continue
            
        # Generate hash to check for duplicates
        article_hash = get_article_hash(article)
        
        # Skip if already processed
        if article_hash in processed_articles:
            continue
            
        # Rewrite the article
        rewritten = rewrite_with_ai(article)
        if not rewritten:
            continue
            
        # Get image
        image_url = get_image_from_article(article)
        
        # Post to Blogger
        if post_to_blogger(rewritten, image_url):
            processed_articles.add(article_hash)
            articles_posted += 1
            
            # Save after each successful post
            save_processed_articles(processed_articles)
            
            # Limit to 3 posts per cycle to avoid API rate limits
            if articles_posted >= 3:
                break
                
            # Wait between posts
            time.sleep(30)
    
    logging.info(f"Posted {articles_posted} new articles")
    
    # Clean up old hashes (keep only the last 1000)
    if len(processed_articles) > 1000:
        processed_articles = set(list(processed_articles)[-1000:])
        save_processed_articles(processed_articles)

def run_scheduler():
    """Run the scheduler to process news every 4 hours."""
    schedule.every(4).hours.do(process_news)
    
    # Run once immediately
    process_news()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logging.info("Starting Science and Technology News Bot")
    run_scheduler()
