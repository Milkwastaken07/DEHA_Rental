import logging
import os
from datetime import datetime

# Set logging level for https://www.en-system.net/admin/tool/index.php
def set_logging():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Set up log file name with timestamp
    # log_file = os.path.join(log_dir, f'scrap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    log_file = os.path.join(log_dir, f'app.log')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # This will output to console
        ]
    )

    # Set logging level for specific modules if needed
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

