from flask import Blueprint, request, jsonify
from db import get_db_connection

family_bp = Blueprint('family', __name__)

@family_bp.route('/<string:email>', methods=['GET'])
def get_family_health(email):
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

        cursor.execute("SELECT relative_type, condition_name FROM family_health WHERE user_id = %s", (user_id,))
        conditions = cursor.fetchall()
        
        # Group by relative
        grouped = {}
        for row in conditions:
            rel = row['relative_type']
            if rel not in grouped:
                grouped[rel] = []
            grouped[rel].append(row['condition_name'])
            
        return jsonify(grouped), 200
    finally:
        cursor.close()
        conn.close()

@family_bp.route('/<string:email>', methods=['POST'])
def update_family_health(email):
    # Expects JSON: { "Father": ["Condition1", "Condition2"], "Mother": [] }
    data = request.json
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

        # Transaction: Delete all for user, then re-insert
        cursor.execute("DELETE FROM family_health WHERE user_id = %s", (user_id,))
        
        for relation, conditions in data.items():
            for condition in conditions:
                cursor.execute(
                    "INSERT INTO family_health (user_id, relative_type, condition_name) VALUES (%s, %s, %s)",
                    (user_id, relation, condition)
                )
        
        conn.commit()
        return jsonify({'message': 'Family health data updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
