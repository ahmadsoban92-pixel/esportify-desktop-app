import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# Import your windows and database connection
from login_main import EsportsLoginWindow
from admin_setup import AdminSetupWindow
from connection import get_db_connection

# Global references to prevent windows from closing instantly (garbage collection)
login_window = None
setup_window = None

def admin_exists():
    """Checks if an admin account already exists in the database."""
    conn = get_db_connection()
    if not conn:
        # If DB connection fails, default to True so it opens the normal login screen
        # where the user can see standard connection errors.
        return True 
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'admin'")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return True

def launch_login():
    """Launches the login screen and closes the setup window if it's open."""
    global login_window, setup_window
    
    login_window = EsportsLoginWindow()
    login_window.show()
    
    if setup_window:
        setup_window.close()

def main():
    global setup_window
    
    # 1. Create the Application
    app = QApplication(sys.argv)

    # 2. Set Global Font
    font = QFont("Inter", 10)
    app.setFont(font)

    # 3. Check Database and Choose Window
    if not admin_exists():
        print("DEBUG: No admin found. Launching First-Run Setup.")
        setup_window = AdminSetupWindow()
        
        # When setup_complete signal is emitted, run the launch_login function
        setup_window.setup_complete.connect(launch_login)
        setup_window.show()
    else:
        print("DEBUG: Admin found. Launching standard Login.")
        launch_login()

    # 4. Start the Event Loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()