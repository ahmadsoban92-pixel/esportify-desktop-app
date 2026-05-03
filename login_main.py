import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QApplication
from PyQt5.QtGui import QPalette, QColor, QLinearGradient, QBrush, QFont
from PyQt5.QtCore import Qt

# --- CUSTOM IMPORTS ---
# Make sure these files exist in your folder
from styles import QSS_STYLES
from Login_Page import Ui_MainWindow
from connection import get_db_connection

# --- ESSENTIAL IMPORT (Moved out of try/except) ---
# This is required for the button to work.
from forgot_password import ForgotPasswordWindow

try:
    from player_register import PlayerRegister
    from referee_register import RefereeRegister
except ImportError:
    print("Warning: Registration modules not found.")

# --- DASHBOARDS (Optional/Work in Progress) ---
try:
    from admin_main import AdminDashboard
    from referee_main import RefereeDashboard
    from player_main import PlayerDashboard
except ImportError:
    print("Warning: Dashboard modules not found.")


class EsportsLoginWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_window_and_palette()
        self.apply_styles()
        self.connect_signals()

        # Window Placeholders
        self.dashboard_window = None
        self.reg_window = None
        self.ref_app_window = None
        self.forgot_window = None

    def initialize_window_and_palette(self):
        self.resize(500, 700)
        self.setWindowTitle("ESPORTIFY - System Login")
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 2, 72))
        gradient.setColorAt(1, QColor(0, 0, 0))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def apply_styles(self):
        # Labels
        self.Esportify_Label.setStyleSheet(QSS_STYLES.get("logo_label", ""))
        self.Login_Label.setStyleSheet(QSS_STYLES.get("title_label", ""))
        self.credentials_label.setStyleSheet(QSS_STYLES.get("subtitle_label", ""))
        self.Email_Label.setStyleSheet(QSS_STYLES.get("standard_label", ""))
        self.Password_Label.setStyleSheet(QSS_STYLES.get("standard_label", ""))

        # Inputs
        self.Input_Email.setStyleSheet(QSS_STYLES.get("input_field", ""))
        self.Input_Password.setStyleSheet(QSS_STYLES.get("input_field", ""))

        # Radio Buttons
        self.Radio_Admin.setStyleSheet(QSS_STYLES.get("radio_button", ""))
        self.Radio_Referee.setStyleSheet(QSS_STYLES.get("radio_button", ""))
        self.Radio_Player.setStyleSheet(QSS_STYLES.get("radio_button", ""))

        # Buttons
        self.Login_Button.setStyleSheet(QSS_STYLES.get("login_button", ""))
        self.CreateAcc_Button.setStyleSheet(QSS_STYLES.get("create_account_button", ""))
        self.ApplyRef_Button.setStyleSheet(QSS_STYLES.get("create_account_button", ""))
        self.ForgotPass_Button.setStyleSheet(QSS_STYLES.get("link_button", "color: blue; border: none;"))

    def connect_signals(self):
        self.Login_Button.clicked.connect(self.handle_login_db)
        self.ForgotPass_Button.clicked.connect(self.open_forgot_password)
        self.CreateAcc_Button.clicked.connect(self.open_player_register)
        self.ApplyRef_Button.clicked.connect(self.open_referee_register)

    # --- WINDOW OPENERS ---
    def open_forgot_password(self):
        # This initializes and shows the Forgot Password Window
        self.forgot_window = ForgotPasswordWindow()
        self.forgot_window.show()

    def open_player_register(self):
        # Check if import succeeded before opening
        if 'PlayerRegister' in globals():
            self.reg_window = PlayerRegister()
            self.reg_window.show()
        else:
            QMessageBox.warning(self, "Error", "Player Register module missing.")

    def open_referee_register(self):
        if 'RefereeRegister' in globals():
            self.ref_app_window = RefereeRegister()
            self.ref_app_window.show()
        else:
            QMessageBox.warning(self, "Error", "Referee Register module missing.")

    # --- DATABASE LOGIN LOGIC ---
    def handle_login_db(self):
        email = self.Input_Email.text().strip()
        password = self.Input_Password.text().strip()

        # 1. Validation
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both Email and Password.")
            return

        # 2. Determine Role and Verify
        success = False
        dashboard_class = None

        if self.Radio_Admin.isChecked():
            if self.verify_credentials("admin", email, password):
                success = True
                if 'AdminDashboard' in globals(): dashboard_class = AdminDashboard

        elif self.Radio_Referee.isChecked():
            # 1. First verify password
            if self.verify_credentials("referee", email, password):
                # 2. Check Approval Status (BEFORE allowing login)
                conn2 = get_db_connection(self)
                if not conn2:
                    return
                try:
                    cursor2 = conn2.cursor()
                    # SQL Syntax for Stored Procedure
                    sql = "{CALL sp_RefereeStatus (?)}"
                    # --- CRITICAL FIX HERE: Add the comma (email,) ---
                    cursor2.execute(sql, (email,))
                    row2 = cursor2.fetchone()

                    # 3. Check what the SP returned
                    # Assuming SP returns a row ONLY if there is a problem (like "Pending")
                    if row2:
                        # Assuming row2.result or row2.Message exists based on your logic
                        if hasattr(row2, 'result') and row2.result == 0:
                            QMessageBox.information(self, "Login Failed", row2.Message)
                            # self.close() # Don't close login window on failure, just return
                            return  # STOP HERE! Do not set success = True

                    # 4. If we passed the check, NOW we allow login
                    conn2.commit()
                    conn2.close()
                    success = True
                    if 'RefereeDashboard' in globals():
                        dashboard_class = RefereeDashboard
                except Exception as e:
                    QMessageBox.critical(self, "Database Error", f"Error checking referee status: {e}")
                    return

        elif self.Radio_Player.isChecked():
            if self.verify_credentials("player", email, password):
                success = True
                if 'PlayerDashboard' in globals(): dashboard_class = PlayerDashboard

        # 3. Launch with Email
        # (This block was previously indented inside Radio_Player, preventing Admin/Ref login)
        if success:
            if dashboard_class:
                # Corrected call: removed 'self' from arguments, added email
                self.launch_dashboard(dashboard_class, email)
            else:
                QMessageBox.warning(self, "Error", "Dashboard file missing or not imported.")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Email, Password, or Role.")

    def verify_credentials(self, role, email, password):
        # We use your existing connection logic
        conn = get_db_connection(self)
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            # Checks the login_check table as per your design
            query = f"SELECT * FROM login_check WHERE email = ? AND password = ? AND role = ?"
            cursor.execute(query, (email, password, role))
            row = cursor.fetchone()
            conn.close()
            return True if row else False

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error verifying user: {e}")
            return False

    # Updated this function to accept the email argument and match class indentation
    def launch_dashboard(self, DashboardClass, user_email):
        try:
            # Pass the email to the Dashboard constructor
            self.dashboard_window = DashboardClass(user_email)

            # Connect logout signal if it exists
            if hasattr(self.dashboard_window, 'logout_signal'):
                self.dashboard_window.logout_signal.connect(self.show_login_screen)

            self.dashboard_window.showMaximized()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Dashboard Error", f"Could not launch dashboard.\n{e}")
            # Print full error for debugging
            import traceback
            traceback.print_exc()

    def show_login_screen(self):
        self.Input_Password.clear()
        self.show()


# Add this to run the file directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EsportsLoginWindow()
    window.show()
    sys.exit(app.exec_())