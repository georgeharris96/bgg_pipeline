# src/utils/loggin_config.py
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set the logging level for httpx to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

