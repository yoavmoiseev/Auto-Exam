"""
Authentication Service
Handles user login, password validation, and session management
Uses SHA-256 hashing (like WEB-ScSc)
"""

import sqlite3
import hashlib
import os
import logging
from config import app_config

logger = logging.getLogger(__name__)

class AuthService:
    """Service for user authentication"""
    
    def __init__(self, db_path=None):
        """Initialize authentication service"""
        if db_path is None:
            db_path = app_config.DATABASE_PATH
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with users table"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode for better concurrency
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            conn.commit()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256 (same as WEB-ScSc)"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def add_user(self, username, password, first_name, last_name, email=None):
        """
        Add new user to database
        Returns: dict with success status
        """
        conn = None
        try:
            password_hash = self._hash_password(password)

            logger.info("Add user attempt - username=%s", username)
            
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode for better concurrency
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, first_name, last_name, email))
            
            user_id = cursor.lastrowid
            conn.commit()

            logger.info("Add user success - username=%s user_id=%s", username, user_id)
            
            return {
                'success': True,
                'message': 'account_created_successfully',
                'user_id': user_id
            }
        except sqlite3.IntegrityError:
            logger.warning("Add user failed - username_exists - username=%s", username)
            return {
                'success': False,
                'message': 'username_already_exists'
            }
        except Exception as e:
            logger.exception("Add user error - username=%s error=%s", username, e)
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}'
            }
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed - add_user - username=%s", username)
    
    def authenticate(self, username, password):
        """
        Authenticate user with username and password
        Returns: dict with success status and user data
        """
        conn = None
        try:
            password_hash = self._hash_password(password)

            logger.info("Authenticate attempt - username=%s", username)
            
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode for better concurrency
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, first_name, last_name, email 
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()

                logger.info("Authenticate success - username=%s user_id=%s", username, user[0])
                
                return {
                    'success': True,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'first_name': user[2],
                        'last_name': user[3],
                        'email': user[4]
                    }
                }
            else:
                logger.warning("Authenticate failed - invalid_credentials - username=%s", username)
                return {
                    'success': False,
                    'message': 'invalid_credentials'
                }
        except Exception as e:
            logger.exception("Authenticate error - username=%s error=%s", username, e)
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed - authenticate - username=%s", username)
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, first_name, last_name, email 
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'first_name': user[2],
                    'last_name': user[3],
                    'email': user[4]
                }
            return None
        except Exception as e:
            logger.exception("Get user error - user_id=%s error=%s", user_id, e)
            return None
        finally:
            if conn:
                conn.close()
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        conn = None
        try:
            # First verify old password
            auth_result = self.authenticate(username, old_password)
            if not auth_result['success']:
                return {
                    'success': False,
                    'message': 'Invalid current password'
                }
            
            new_password_hash = self._hash_password(new_password)
            
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ? 
                WHERE username = ?
            ''', (new_password_hash, username))
            
            conn.commit()
            
            logger.info("Password changed - username=%s", username)
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
        except Exception as e:
            logger.exception("Change password error - username=%s error=%s", username, e)
            return {
                'success': False,
                'message': f'Error changing password: {str(e)}'
            }
        finally:
            if conn:
                conn.close()
