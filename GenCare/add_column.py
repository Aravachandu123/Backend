import mysql.connector
from db import get_db_connection

def update_schema():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()
    try:
        print("Adding is_profile_complete column to users table...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN is_profile_complete BOOLEAN DEFAULT FALSE;
        """)
        conn.commit()
        print("Successfully added is_profile_complete column.")
        
        # Update existing dummy users to be complete for testing
        print("Updating existing users to be complete...")
        cursor.execute("UPDATE users SET is_profile_complete = TRUE WHERE email IN ('ethan@example.com', 'sophia@example.com', 'marcus@example.com');")
        conn.commit()
        print("Updated dummy users.")
        
    except mysql.connector.Error as err:
        if "Duplicate column name" in str(err):
            print("Column is_profile_complete already exists.")
        else:
            print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
