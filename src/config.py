"""Configuration management for BizHub - supports local and cloud deployments."""
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'
DB_URL = os.getenv('DB_URL', 'inventory.db')
DB_FILE = os.getenv('DB_FILE', 'inventory.db')

# Application mode
MODE = os.getenv('MODE', 'desktop')  # 'desktop' or 'web' or 'api'

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = os.getenv('SMTP_PORT', 587)
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')

# Cloud settings (future)
CLOUD_ENABLED = os.getenv('CLOUD_ENABLED', 'false').lower() == 'true'
CLOUD_API_URL = os.getenv('CLOUD_API_URL', '')

# Debug mode
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Default admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Application settings
APP_NAME = 'Bzhub'
APP_VERSION = '1.0.0'

def get_db_config():
    """Get database configuration based on mode."""
    if DB_TYPE == 'sqlite':
        return {'type': 'sqlite', 'path': DB_FILE}
    elif DB_TYPE == 'postgresql':
        return {'type': 'postgresql', 'url': DB_URL}
    else:
        raise ValueError(f"Unknown DB_TYPE: {DB_TYPE}")
