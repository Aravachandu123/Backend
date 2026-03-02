import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),        # Default XAMPP user
    'password': os.getenv('DB_PASSWORD', ''),    # Default XAMPP password (empty)
    'database': os.getenv('DB_NAME', 'gencare_db'),
    'port': int(os.getenv('DB_PORT', 3308))      # XAMPP MySQL configured to 3308
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
