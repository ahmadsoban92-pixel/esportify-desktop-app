import os
import pyodbc
from PyQt5.QtWidgets import QMessageBox
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_db_connection(parent=None):
    """
    Establishes a connection to the SQL Server database.
    If parent is provided, shows a popup on error.
    Otherwise, prints the error to the console.
    """
    try:
        # --- CONFIGURATION (Securely loaded from .env) ---
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASS = os.getenv('DB_PASS')

        # Failsafe: Check if the variables actually loaded
        if not server or not database:
            raise ValueError("Database credentials not found. Make sure your .env file exists and is named correctly.")

        # --- CONNECTION STRING ---
        connection_string = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={DB_USER};'
            f'PWD={DB_PASS};'
        )

        conn = pyodbc.connect(connection_string)
        return conn

    except Exception as e:
        error_msg = f"Failed to connect to Database.\nError: {e}"

        # If a parent window (like Login or Register) passed itself in, show a popup
        if parent:
            QMessageBox.critical(parent, "Connection Error", error_msg)
        else:
            print(error_msg)

        return None