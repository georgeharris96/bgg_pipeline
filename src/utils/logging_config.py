# src/utils/loggin_config.py
import logging

def setup_logging():
    handlers = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler("app.log"))
    except OSError:
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
    
    # Set the logging level for httpx to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

