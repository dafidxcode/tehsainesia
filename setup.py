import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for Google API
SCOPES = ['https://www.googleapis.com/auth/blogger']

def setup_blogger_auth():
    """Set up Blogger API authentication."""
    print("Setting up Blogger API authentication...")
    
    # Get client ID and client secret
    client_id = "391743657244-st5hh83vjm14ihkf7t12iabj5bf6mqpp.apps.googleusercontent.com"
    client_secret = "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"
    
    # Create credentials file
    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    with open("blogger_credentials.json", "w") as f:
        json.dump(credentials, f)
    
    # Run the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        "blogger_credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save the credentials
    with open("token.pickle", "wb") as f:
        pickle.dump(creds, f)
    
    print("Authentication successful!")
    
    # Get the blog ID
    service = build('blogger', 'v3', credentials=creds)
    blogs = service.blogs().listByUser(userId='self').execute()
    
    if not blogs.get('items'):
        print("No blogs found for this account!")
        return
    
    print("\nAvailable blogs:")
    for i, blog in enumerate(blogs['items']):
        print(f"{i+1}. {blog['name']} (ID: {blog['id']})")
    
    selection = int(input("\nSelect a blog by number: ")) - 1
    blog_id = blogs['items'][selection]['id']
    
    # Create config file
    config = {
        "BLOG_ID": blog_id,
        "NEWS_API_KEY": "584c30f792ff4d4c9fa1040ee842122e",
        "OPENAI_API_KEY": "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"
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f)
    
    print("\nSetup complete! You can now run the news_aggregator.py script.")

if __name__ == "__main__":
    setup_blogger_auth()
    