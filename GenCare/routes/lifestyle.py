from flask import Blueprint, request, jsonify
from db import get_db_connection

lifestyle_bp = Blueprint('lifestyle', __name__)

@lifestyle_bp.route('/<string:email>', methods=['GET'])
def get_lifestyle(email):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user_id from email first
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user_id = user['id']

        cursor.execute("SELECT * FROM lifestyle WHERE user_id = %s", (user_id,))
        lifestyle = cursor.fetchone()
        if lifestyle:
            return jsonify(lifestyle), 200
        return jsonify({'error': 'Lifestyle data not found'}), 404
    finally:
        cursor.close()
        conn.close()

@lifestyle_bp.route('/<string:email>', methods=['PUT'])
def update_lifestyle(email):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor()
    
    try:
        # Get user_id from email first
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user_id = user[0] # cursor is not dictionary=True here

        fields = []
        values = []
        allowed_fields = ['activity_level', 'diet_type', 'smoking_status', 'high_salt']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not fields:
            return jsonify({'message': 'No fields to update'}), 200
            
        values.append(user_id)
        # Check if exists first
        cursor.execute("SELECT id FROM lifestyle WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            query = f"UPDATE lifestyle SET {', '.join(fields)} WHERE user_id = %s"
            cursor.execute(query, tuple(values))
        else:
            # Insert if not exists
            cols = ['user_id'] + [f for f in allowed_fields if f in data]
            placeholders = ['%s'] * len(cols)
            vals = [user_id] + [data[f] for f in allowed_fields if f in data]
            query = f"INSERT INTO lifestyle ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, tuple(vals))
            
        conn.commit()
        return jsonify({'message': 'Lifestyle updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
