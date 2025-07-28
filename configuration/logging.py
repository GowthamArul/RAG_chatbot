import logging
import os

def init_logger(log_file='../logs/app.log'):

    log_path = os.path.abspath(os.path.dirname(__file__), log_file)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )