from flask import Blueprint, request, jsonify
from db import get_db_connection

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/<string:email>', methods=['GET'])
def get_user_logs(email):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        # Get user_id from email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user_id = user['id']

        cursor.execute("SELECT * FROM user_logs WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (user_id,))
        logs = cursor.fetchall()
        return jsonify(logs), 200
    finally:
        cursor.close()
        conn.close()

@logs_bp.route('/', methods=['POST'])
def add_log():
    data = request.json
    email = data.get('email')
    title = data.get('title')
    subtitle = data.get('subtitle')
    icon = data.get('icon', 'circle.fill')
    color = data.get('color', '#000000')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor()
    try:
        # Get user_id from email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user_id = user[0]

        cursor.execute(
            "INSERT INTO user_logs (user_id, action_title, action_subtitle, icon, color_hex) VALUES (%s, %s, %s, %s, %s)",
            (user_id, title, subtitle, icon, color)
        )
        conn.commit()
        return jsonify({'message': 'Log added'}), 201
    finally:
        cursor.close()
        conn.close()

@logs_bp.route('/<string:email>', methods=['DELETE'])
def clear_user_logs(email):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor()
    try:
        # Get user_id from email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user_id = user[0]

        cursor.execute("DELETE FROM user_logs WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': 'Logs cleared successfully'}), 200
    finally:
        cursor.close()
        conn.close()
