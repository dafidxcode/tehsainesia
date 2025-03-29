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