import sqlite3
import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path: str = "id_card_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_code TEXT UNIQUE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_by INTEGER,
                used_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id),
                FOREIGN KEY (used_by) REFERENCES users (user_id)
            )
        ''')
        
        # ID Cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS id_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                college TEXT NOT NULL,
                department TEXT NOT NULL,
                issue_authority TEXT NOT NULL,
                qr_data TEXT NOT NULL,
                card_path TEXT NOT NULL,
                token_used TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create admin user (itzAyush)
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (123456789, 'itzAyush', 'Ayush', True))  # Placeholder user_id, will be updated when admin first uses bot
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user is admin
        is_admin = username == 'itzAyush'
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, is_admin))
        
        conn.commit()
        conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0]
    
    def create_token(self, token_code: str, created_by: int) -> bool:
        """Create a new token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tokens (token_code, created_by)
                VALUES (?, ?)
            ''', (token_code, created_by))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Token already exists
    
    def use_token(self, token_code: str, user_id: int) -> bool:
        """Use a token if it's valid and unused"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if token exists and is unused
        cursor.execute('''
            SELECT id FROM tokens 
            WHERE token_code = ? AND is_used = FALSE
        ''', (token_code,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        # Mark token as used
        cursor.execute('''
            UPDATE tokens 
            SET is_used = TRUE, used_by = ?, used_at = CURRENT_TIMESTAMP
            WHERE token_code = ?
        ''', (user_id, token_code))
        
        conn.commit()
        conn.close()
        return True
    
    def save_id_card(self, user_id: int, student_name: str, father_name: str, 
                     phone: str, college: str, department: str, issue_authority: str,
                     qr_data: str, card_path: str, token_used: str):
        """Save ID card information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO id_cards 
            (user_id, student_name, father_name, phone, college, department, 
             issue_authority, qr_data, card_path, token_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, student_name, father_name, phone, college, department,
              issue_authority, qr_data, card_path, token_used))
        
        conn.commit()
        conn.close()
    
    def get_all_id_cards(self) -> List[Dict]:
        """Get all ID cards for admin view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ic.*, u.username, u.first_name
            FROM id_cards ic
            JOIN users u ON ic.user_id = u.user_id
            ORDER BY ic.created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_user_id_cards(self, user_id: int) -> List[Dict]:
        """Get ID cards for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM id_cards 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_token_stats(self) -> Dict:
        """Get token statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tokens')
        total_tokens = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tokens WHERE is_used = TRUE')
        used_tokens = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tokens': total_tokens,
            'used_tokens': used_tokens,
            'available_tokens': total_tokens - used_tokens
        }

