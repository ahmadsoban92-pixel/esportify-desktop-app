import sys
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QStackedWidget, QApplication)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtWidgets  # Needed for icons
from styles import QSS_STYLES
from connection import get_db_connection
from otp_gen import send_otp_email


class PlayerRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Account")
        self.setFixedSize(450, 660)
        self.setStyleSheet(
            QSS_STYLES.get("window_background", "background-color: #0f0b12; color: white; font-family: Segoe UI;"))

        # --- STATE VARIABLES ---
        self.generated_otp = None
        self.pending_data = None

        # --- MAIN LAYOUT WITH STACK ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Initialize Pages
        self.init_register_page()
        self.init_otp_page()

        # Show Register Page first
        self.stack.setCurrentIndex(0)

    # ------------------------------------
    # PAGE 1: REGISTRATION FORM
    # ------------------------------------
    def init_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(10)

        # Header
        lbl_title = QLabel("JOIN ESPORTIFY")
        lbl_title.setStyleSheet(QSS_STYLES.get("logo_label", "font-size: 24px; font-weight: bold; color: #E0E0E0;"))
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Create your player profile below")
        lbl_subtitle.setStyleSheet("color: #a0a0a0; font-size: 13px; margin-bottom: 10px;")
        lbl_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_subtitle)

        # Form Layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        # Inputs
        self.input_username = self.create_input("Username:", "Enter unique username", form_layout)
        self.input_gamertag = self.create_input("Gamertag:", "e.g. Slayer_99", form_layout)
        self.input_cnic = self.create_input("CNIC:", "35202-1234567-8", form_layout)
        self.input_email = self.create_input("Email Address:", "user@gmail.com", form_layout)

        # Password Field
        self.lbl_pass = QLabel("Password:")
        self.lbl_pass.setStyleSheet(QSS_STYLES.get("standard_label", "font-size: 14px; color: #E0E0E0;"))
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setStyleSheet(QSS_STYLES.get("input_field", "padding: 8px; border-radius: 4px;"))
        form_layout.addWidget(self.lbl_pass)
        form_layout.addWidget(self.input_pass)

        # --- ADD EYE TOGGLE HERE ---
        self.add_password_toggle(self.input_pass)

        layout.addLayout(form_layout)

        # Register Button
        btn_register = QPushButton("VERIFY & CREATE")
        btn_register.setCursor(Qt.PointingHandCursor)
        btn_register.setStyleSheet(
            QSS_STYLES.get("login_button", "padding: 10px; background-color: #6200ea; color: white;"))
        btn_register.clicked.connect(self.handle_initial_validation)
        layout.addWidget(btn_register)

        self.stack.addWidget(page)

    def create_input(self, label_text, placeholder, parent_layout):
        lbl = QLabel(label_text)
        lbl.setStyleSheet(QSS_STYLES.get("standard_label", "font-size: 14px; color: #E0E0E0;"))
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(QSS_STYLES.get("input_field", "padding: 8px; border-radius: 4px;"))
        parent_layout.addWidget(lbl)
        parent_layout.addWidget(inp)
        return inp

    # --- EYE TOGGLE HELPERS (Added) ---
    def add_password_toggle(self, line_edit):
        action = line_edit.addAction(self.get_eye_icon(False), QLineEdit.TrailingPosition)
        action.triggered.connect(lambda: self.toggle_password_visibility(line_edit, action))

    def toggle_password_visibility(self, line_edit, action):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            action.setIcon(self.get_eye_icon(True))
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            action.setIcon(self.get_eye_icon(False))

    def get_eye_icon(self, is_open):
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        if is_open:
            painter.setPen(QtGui.QColor("#4caf50"))
            text = "O"
        else:
            painter.setPen(QtGui.QColor("#a0a0a0"))
            text = "Ø"
        font = QtGui.QFont("Arial", 14, QtGui.QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        return QtGui.QIcon(pixmap)

    # ------------------------------------
    # PAGE 2: OTP VERIFICATION (Unchanged)
    # ------------------------------------
    def init_otp_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Email Verification")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)

        self.lbl_otp_msg = QLabel("Enter the code sent to your email.")
        self.lbl_otp_msg.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        self.lbl_otp_msg.setAlignment(Qt.AlignCenter)

        self.input_otp = QLineEdit()
        self.input_otp.setPlaceholderText("XXXXXX")
        self.input_otp.setAlignment(Qt.AlignCenter)
        self.input_otp.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e; color: white; border: 2px solid #6200ea;
                border-radius: 8px; padding: 10px; font-size: 18px; letter-spacing: 5px;
            }
        """)

        btn_verify = QPushButton("Verify Code")
        btn_verify.setCursor(Qt.PointingHandCursor)
        btn_verify.setStyleSheet(
            QSS_STYLES.get("login_button", "padding: 10px; background-color: #6200ea; color: white;"))
        btn_verify.clicked.connect(self.handle_otp_verification)

        btn_back = QPushButton("Back to Edit")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("background: transparent; color: #a0a0a0; text-decoration: underline;")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(title)
        layout.addWidget(self.lbl_otp_msg)
        layout.addSpacing(20)
        layout.addWidget(self.input_otp)
        layout.addWidget(btn_verify)
        layout.addWidget(btn_back)

        self.stack.addWidget(page)

    # ------------------------------------
    # LOGIC: VALIDATION & EMAIL SENDING (Unchanged)
    # ------------------------------------
    def handle_initial_validation(self):
        username = self.input_username.text().strip()
        tag = self.input_gamertag.text().strip()
        cnic = self.input_cnic.text().strip()
        email = self.input_email.text().strip()
        password = self.input_pass.text()

        if not username or not tag or not cnic or not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return
        if not re.match(r"^[A-Za-z ]+$", username):
            QMessageBox.warning(self, "Invalid Name", "Name can only contain letters and spaces.")
            return
        if not re.match(r"^[a-zA-Z0-9_]+$", tag):
            QMessageBox.warning(self, "Invalid Gamertag",
                                "Gamertag can only contain letters, numbers, and underscores.")
            return
        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            QMessageBox.warning(self, "Invalid Email", "Only @gmail.com allowed.")
            return
        if not re.match(r"^\d{5}-\d{7}-\d{1}$", cnic):
            QMessageBox.warning(self, "Invalid CNIC", "CNIC must follow the format:\n12345-1234567-1")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long.")
            return

        if self.is_email_taken(email):
            QMessageBox.warning(self, "Error", "This email is already registered.")
            return

        self.pending_data = (username, tag, email, password, cnic)
        self.trigger_otp_send(email)

    def is_email_taken(self, email):
        conn = get_db_connection(self)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM Users WHERE email = ?", (email,))
                exists = cursor.fetchone()
                conn.close()
                return exists is not None
            except:
                return False
        return False

    def trigger_otp_send(self, to_mail):
        otp_code = send_otp_email(to_mail, subject="ESPORTIFY - Registration OTP")
        if otp_code:
            self.generated_otp = otp_code
            self.lbl_otp_msg.setText(f"Code sent to {to_mail}")
            self.stack.setCurrentIndex(1)
        else:
            QMessageBox.critical(self, "Connection Error", "Failed to send email.\nCheck internet connection.")

    # ------------------------------------
    # LOGIC: OTP VERIFICATION & FINAL SAVE (Unchanged)
    # ------------------------------------
    def handle_otp_verification(self):
        user_input = self.input_otp.text().strip()

        if user_input == self.generated_otp:
            self.create_account_in_db()
        else:
            QMessageBox.warning(self, "Error", "Invalid OTP. Please try again.")

    def create_account_in_db(self):
        if not self.pending_data: return
        username, tag, email, password, cnic = self.pending_data

        conn = get_db_connection(self)
        if conn:
            try:
                cursor = conn.cursor()
                sql_command = "{CALL sp_RegisterPlayer (?, ?, ?, ?, ?)}"
                parameters = (username, tag, email, password, cnic)
                cursor.execute(sql_command, parameters)
                row = cursor.fetchone()
                if row and row.Result == 1:
                    conn.commit()
                    QMessageBox.information(self, "Welcome", "Account Created Successfully!\nYou can now login.")
                    self.close()
                else:
                    msg = row.Message if row else "Unknown Database Error"
                    QMessageBox.warning(self, "Registration Failed", msg)
                    self.stack.setCurrentIndex(0)
                conn.close()
            except Exception as e:
                if "UNIQUE KEY" in str(e):
                    QMessageBox.warning(self, "Error", "Gamertag or CNIC is already taken.")
                else:
                    QMessageBox.critical(self, "Database Error", f"Error: {e}")
                self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlayerRegister()
    window.show()
    sys.exit(app.exec_())