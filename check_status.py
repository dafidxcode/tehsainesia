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