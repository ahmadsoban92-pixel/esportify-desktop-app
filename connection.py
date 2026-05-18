import os
import pyodbc
from PyQt5.QtWidgets import QMessageBox
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_db_connection(parent=None):
    """
    Establishes a connection to the SQL Server database dynamically.
    Supports both Client-Server (SQL Auth) and Local Machine (Windows Auth).
    """
    try:
        # --- CONFIGURATION (Securely loaded from .env) ---
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')

        # Failsafe: Server and Database name are always required
        if not server or not database:
            raise ValueError("Database credentials not found. Make sure your .env file exists and has DB_SERVER and DB_NAME.")

        # --- CONNECTION STRING LOGIC ---
        
        # Scenario A: Client-Server Setup (Explicit SQL Authentication)
        if db_user and db_pass:
            connection_string = (
                f'DRIVER={{SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={db_user};'
                f'PWD={db_pass};'
            )
            
        # Scenario B: Simple Local Setup (Windows Authentication Fallback)
        else:
            connection_string = (
                f'DRIVER={{SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'Trusted_Connection=yes;'
            )

        conn = pyodbc.connect(connection_string)
        return conn

    except Exception as e:
        error_msg = f"Failed to connect to Database.\nError: {e}"

        # If a parent window passed itself in, show a popup
        if parent:
            QMessageBox.critical(parent, "Connection Error", error_msg)
        else:
            print(error_msg)

        return None