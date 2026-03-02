from flask import Blueprint, request, jsonify
from db import get_db_connection

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
def get_all_users():
    """Fetch a list of all users (for testing/admin purposes)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, full_name, email, age, gender FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200
    finally:
        cursor.close()
        conn.close()

@profile_bp.route('/<string:email>', methods=['GET'])
def get_profile(email):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, full_name, email, phone, age, gender, blood_type FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    finally:
        cursor.close()
        conn.close()

@profile_bp.route('/<string:email>', methods=['PUT'])
def update_profile(email):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor()
    
    try:
        # Construct update query dynamically
        fields = []
        values = []
        allowed_fields = ['full_name', 'phone', 'age', 'gender', 'blood_type']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not fields:
            return jsonify({'message': 'No fields to update'}), 200
            
        values.append(email)
        query = f"UPDATE users SET {', '.join(fields)} WHERE email = %s"
        
        cursor.execute(query, tuple(values))
        conn.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
