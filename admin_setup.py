import sys
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from connection import get_db_connection
from otp_gen import send_otp_email  # Import your OTP generator

class AdminSetupWindow(QtWidgets.QMainWindow):
    # This signal tells the main script that setup is done so it can load the Login screen
    setup_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Esportify - First Run Setup")
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: #1e1e21; color: white; font-family: Arial;")

        self.init_ui()

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Title
        lbl_title = QtWidgets.QLabel("Welcome to Esportify!")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #bd93f9;")
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_desc = QtWidgets.QLabel("No admin account detected. Please create the master administrator account to continue.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 14px; color: #a0a0a0; margin-bottom: 20px;")
        lbl_desc.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_desc)

        # Input Fields
        self.inputs = {}
        fields = [
            ("Name", "Enter full name (Letters only)", False),
            ("Email", "Must end in @gmail.com", False),
            ("Password", "Minimum 8 characters", True),
            ("CNIC", "Format: 12345-1234567-1", False)
        ]

        for label_text, placeholder, is_password in fields:
            lbl = QtWidgets.QLabel(label_text)
            lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(lbl)

            line_edit = QtWidgets.QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2d; border: 2px solid #444; 
                    border-radius: 6px; padding: 10px; font-size: 14px;
                }
                QLineEdit:focus { border: 2px solid #bd93f9; }
            """)
            if is_password:
                line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
            
            self.inputs[label_text] = line_edit
            layout.addWidget(line_edit)

        # Submit Button
        self.btn_submit = QtWidgets.QPushButton("Create Admin & Launch")
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #7b2cbf; color: white; font-weight: bold;
                border-radius: 6px; padding: 12px; font-size: 16px; margin-top: 20px;
            }
            QPushButton:hover { background-color: #9d4edd; }
            QPushButton:disabled { background-color: #555555; color: #888888; }
        """)
        self.btn_submit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_submit.clicked.connect(self.verify_and_create_admin)
        layout.addWidget(self.btn_submit)

        layout.addStretch()

    def verify_and_create_admin(self):
        name = self.inputs["Name"].text().strip()
        email = self.inputs["Email"].text().strip()
        password = self.inputs["Password"].text()
        cnic = self.inputs["CNIC"].text().strip()

        # --- VALIDATION (Matching your SQL constraints) ---
        if not all([name, email, password, cnic]):
            QtWidgets.QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if not re.match(r"^[A-Za-z ]+$", name):
            QtWidgets.QMessageBox.warning(self, "Error", "Name can only contain letters and spaces.")
            return

        if not email.endswith("@gmail.com") or " " in email or email.count("@") > 1:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid email format. Must be a valid @gmail.com address.")
            return

        if len(password) < 8:
            QtWidgets.QMessageBox.warning(self, "Error", "Password must be at least 8 characters long.")
            return

        if not re.match(r"^\d{5}-\d{7}-\d{1}$", cnic):
            QtWidgets.QMessageBox.warning(self, "Error", "CNIC must follow the format: XXXXX-XXXXXXX-X")
            return

        # --- OTP VERIFICATION ---
        # Temporarily disable the button so the user doesn't spam click it
        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Sending OTP...")
        QtWidgets.QApplication.processEvents()  # Force UI to update text immediately

        # Send the email
        generated_otp = send_otp_email(email, "Esportify Master Admin Setup")

        # Re-enable the button
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Create Admin & Launch")

        if not generated_otp:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to send OTP. Please check your internet connection or email configuration in .env.")
            return

        # Ask user for the OTP
        user_input, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Email Verification", 
            f"An OTP has been sent to {email}.\n\nPlease enter the 6-digit code:"
        )

        if ok:
            if user_input.strip() == generated_otp:
                # OTP is correct, proceed to database insertion
                self.insert_admin_to_db(name, email, password, cnic)
            else:
                QtWidgets.QMessageBox.warning(self, "Verification Failed", "Incorrect OTP. Admin setup aborted.")

    def insert_admin_to_db(self, name, email, password, cnic):
        # --- DATABASE INSERTION ---
        conn = get_db_connection(self)
        if not conn: return

        try:
            cursor = conn.cursor()
            
            # Note: For production, you should hash this password!
            query = """
                INSERT INTO Users (name, email, password, CNIC, role)
                VALUES (?, ?, ?, ?, 'admin')
            """
            cursor.execute(query, (name, email, password, cnic))
            conn.commit()

            QtWidgets.QMessageBox.information(self, "Success", "Admin account created and verified successfully!\n\nLaunching login...")
            self.setup_complete.emit() # Signal main_whole.py to open the login screen
            self.close()

        except Exception as e:
            conn.rollback()
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Failed to create admin:\n{e}")
        finally:
            conn.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminSetupWindow()
    window.show()
    sys.exit(app.exec_())