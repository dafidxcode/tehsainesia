import os
import sys
import time
from subprocess import Popen
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("service_monitor.log"),
        logging.StreamHandler()
    ]
)

def run_bot():
    """Run the news bot and monitor it."""
    while True:
        logging.info("Starting news bot process...")
        
        # Start the bot process
        process = Popen([sys.executable, 'news_aggregator.py'])
        
        # Monitor the process
        try:
            # Wait for the process to terminate
            process.wait()
            logging.warning("News bot process terminated unexpectedly. Restarting in 60 seconds...")
            time.sleep(60)
        except KeyboardInterrupt:
            # Handle manual termination
            process.terminate()
            logging.info("News bot service stopped by user.")
            break
        except Exception as e:
            # Handle other exceptions
            logging.error(f"Error in monitor: {str(e)}")
            if process.poll() is None:
                process.terminate()
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
