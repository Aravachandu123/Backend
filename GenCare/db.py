import mysql.connector

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',        # Default XAMPP user
    'password': '',        # Default XAMPP password (empty)
    'database': 'gencare_db',
    'port': 3308           # XAMPP MySQL configured to 3308
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
