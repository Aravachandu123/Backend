from flask import Blueprint, jsonify
from db import get_db_connection
import json

risk_history_bp = Blueprint('risk_history', __name__)

@risk_history_bp.route('/<email>', methods=['GET'])
def get_risk_history(email):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # 1. Fetch user_id
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({"error": "User not found"}), 404
            
        user_id = user_row['id']
        
        # 2. Fetch last 10 records
        cursor.execute("""
            SELECT id, overall_risk_percent, overall_risk_level, dominant_category, risk_breakdown, response_json, created_at
            FROM risk_history 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (user_id,))
        
        records = cursor.fetchall()
        
        # Convert JSON strings to Python objects
        for r in records:
            if isinstance(r['risk_breakdown'], str):
                r['risk_breakdown'] = json.loads(r['risk_breakdown'])
            if isinstance(r['response_json'], str):
                r['response_json'] = json.loads(r['response_json'])
                
        return jsonify(records), 200
        
    except Exception as e:
        print(f"Error fetching risk history: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
