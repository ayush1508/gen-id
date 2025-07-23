import os
import sys
import sqlite3
import uuid
import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash

admin_bp = Blueprint('admin', __name__)

# Admin credentials (in production, use proper authentication)
ADMIN_USERNAME = "itzAyush"
ADMIN_PASSWORD = "admin123"  # Change this in production

def get_bot_db_connection():
    """Get connection to the bot's database"""
    bot_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'id_card_bot.db')
    return sqlite3.connect(bot_db_path)

def generate_token_code():
    """Generate a random token code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': 'admin_session_token'  # In production, use proper JWT
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get bot statistics"""
    try:
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        # Get token statistics
        cursor.execute('SELECT COUNT(*) FROM tokens')
        total_tokens = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tokens WHERE is_used = TRUE')
        used_tokens = cursor.fetchone()[0]
        
        # Get ID card statistics
        cursor.execute('SELECT COUNT(*) FROM id_cards')
        total_cards = cursor.fetchone()[0]
        
        # Get user statistics
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Get recent activity (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM id_cards 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        recent_cards = cursor.fetchone()[0]
        
        # College distribution
        cursor.execute('''
            SELECT college, COUNT(*) as count 
            FROM id_cards 
            GROUP BY college 
            ORDER BY count DESC
        ''')
        college_stats = [{'college': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'tokens': {
                    'total': total_tokens,
                    'used': used_tokens,
                    'available': total_tokens - used_tokens
                },
                'cards': {
                    'total': total_cards,
                    'recent': recent_cards
                },
                'users': {
                    'total': total_users
                },
                'college_distribution': college_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@admin_bp.route('/tokens', methods=['POST'])
def generate_tokens():
    """Generate new tokens"""
    try:
        data = request.get_json()
        count = data.get('count', 10)
        
        if count > 100:
            return jsonify({
                'success': False,
                'message': 'Cannot generate more than 100 tokens at once'
            }), 400
        
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        generated_tokens = []
        for _ in range(count):
            token_code = generate_token_code()
            try:
                cursor.execute('''
                    INSERT INTO tokens (token_code, created_by)
                    VALUES (?, ?)
                ''', (token_code, 123456789))  # Admin user ID
                generated_tokens.append(token_code)
            except sqlite3.IntegrityError:
                # Token already exists, try again
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_tokens)} tokens',
            'tokens': generated_tokens
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating tokens: {str(e)}'
        }), 500

@admin_bp.route('/cards', methods=['GET'])
def get_all_cards():
    """Get all ID cards"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM id_cards')
        total_cards = cursor.fetchone()[0]
        
        # Get paginated cards
        cursor.execute('''
            SELECT ic.*, u.username, u.first_name
            FROM id_cards ic
            LEFT JOIN users u ON ic.user_id = u.user_id
            ORDER BY ic.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        columns = [description[0] for description in cursor.description]
        cards = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'cards': cards,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_cards,
                    'pages': (total_cards + per_page - 1) // per_page
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching cards: {str(e)}'
        }), 500

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    try:
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, COUNT(ic.id) as card_count
            FROM users u
            LEFT JOIN id_cards ic ON u.user_id = ic.user_id
            GROUP BY u.user_id
            ORDER BY u.created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': users
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }), 500

@admin_bp.route('/tokens/unused', methods=['GET'])
def get_unused_tokens():
    """Get unused tokens"""
    try:
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT token_code, created_at
            FROM tokens
            WHERE is_used = FALSE
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        
        tokens = [{'code': row[0], 'created_at': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': tokens
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching tokens: {str(e)}'
        }), 500

@admin_bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete an ID card"""
    try:
        conn = get_bot_db_connection()
        cursor = conn.cursor()
        
        # Get card info first
        cursor.execute('SELECT card_path FROM id_cards WHERE id = ?', (card_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Card not found'
            }), 404
        
        card_path = result[0]
        
        # Delete from database
        cursor.execute('DELETE FROM id_cards WHERE id = ?', (card_id,))
        conn.commit()
        conn.close()
        
        # Delete file if exists
        try:
            if os.path.exists(card_path):
                os.remove(card_path)
        except Exception:
            pass  # Ignore file deletion errors
        
        return jsonify({
            'success': True,
            'message': 'Card deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting card: {str(e)}'
        }), 500

