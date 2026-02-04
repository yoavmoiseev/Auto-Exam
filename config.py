"""
Configuration file for Exam System Flask App
Supports both Web and Standalone offline modes
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-exam-system-secret-key-change-in-production'
    DEBUG = False
    
    # Session configuration
    SESSION_COOKIE_NAME = 'exam_session'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # False for offline mode (no HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = None  # Allow cookies through nginx proxy
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_DOMAIN = None  # Let Flask auto-detect
    
    # Database paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    TEACHERS_DIR = os.path.join(BASE_DIR, 'teachers')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Database
    DATABASE_PATH = os.path.join(DATA_DIR, 'users.db')
    
    # Upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Languages supported
    SUPPORTED_LANGUAGES = ['en', 'ru', 'he']
    DEFAULT_LANGUAGE = 'en'
    
    # Exam settings
    DEFAULT_TIMER_MINUTES = 60
    DEFAULT_MAX_QUESTIONS = 1000
    
    # Proctoring settings
    TRACK_IP = True
    TRACK_USER_AGENT = True
    MAX_PAGE_REFRESHES = 5  # Allow max 5 refreshes before alert
    

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration (when deployed)"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Use HTTPS in production
    

class StandaloneConfig(Config):
    """Configuration for standalone offline exe"""
    DEBUG = False
    SESSION_COOKIE_SECURE = False
    # All paths are relative to exe location
    

# Select config based on environment
ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')

if ENVIRONMENT == 'production':
    app_config = ProductionConfig()
elif ENVIRONMENT == 'standalone':
    app_config = StandaloneConfig()
else:
    app_config = DevelopmentConfig()
