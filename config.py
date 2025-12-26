import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Database
    DB_PATH = os.getenv('DB_PATH', 'data/titanium_clinica.db')
    
    # App
    APP_NAME = "Titanium Clínica"
    APP_VERSION = "2.0.0"
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    
    # WhatsApp
    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    
    # Limits
    MAX_DAILY_CONTACTS = 30
    MIN_INTERVAL_SECONDS = 120
    WORKING_HOURS_START = 8
    WORKING_HOURS_END = 20
    
    # Backup
    BACKUP_AUTO = True
    BACKUP_HOUR = 23
    BACKUP_RETENTION_DAYS = 7

config = Config()