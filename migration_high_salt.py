import mysql.connector
from db import get_db_connection

def run_migration():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        return
        
    cursor = conn.cursor()
    try:
        # Check if the column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'gencare_db' 
            AND TABLE_NAME = 'lifestyle' 
            AND COLUMN_NAME = 'high_salt'
        """)
        
        result = cursor.fetchone()
        if not result:
            print("Adding 'high_salt' column to 'lifestyle' table...")
            cursor.execute("ALTER TABLE lifestyle ADD COLUMN high_salt BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'high_salt' already exists. Skipping migration.")
            
    except Exception as e:
        print(f"Error running migration: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
