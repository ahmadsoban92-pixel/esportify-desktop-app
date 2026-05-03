import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtWidgets  # Needed for icons
from styles import QSS_STYLES

# 1. IMPORT CONNECTION & UTILS
from connection import get_db_connection
from otp_gen import send_otp_email


class ForgotPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset Password")
        self.resize(400, 350)
        self.setStyleSheet(
            QSS_STYLES.get("window_background", "background-color: #0f0b12; color: white; font-family: Segoe UI;"))

        self.generated_otp = None
        self.rec_email = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.init_email_page()
        self.init_otp_page()
        self.init_reset_page()

    # (Keep init_email_page and init_otp_page EXACTLY as they were)
    def init_email_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Reset Password")
        title.setStyleSheet(QSS_STYLES.get("title_label", "font-size: 24px; font-weight: bold; color: #E0E0E0;"))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Enter your email to receive an OTP.")
        subtitle.setStyleSheet(QSS_STYLES.get("subtitle_label", "font-size: 14px; color: #A0A0A0;"))
        subtitle.setAlignment(Qt.AlignCenter)
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Enter your email")
        self.input_email.setStyleSheet(QSS_STYLES.get("input_field",
                                                      "padding: 10px; border: 1px solid #555; border-radius: 5px; background-color: #1e1e1e; color: white;"))
        btn_next = QPushButton("Send OTP")
        btn_next.setCursor(Qt.PointingHandCursor)
        btn_next.setStyleSheet(QSS_STYLES.get("login_button",
                                              "padding: 10px; background-color: #6200ea; color: white; border-radius: 5px; font-weight: bold;"))
        btn_next.clicked.connect(self.handle_send_otp)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.input_email)
        layout.addWidget(btn_next)
        layout.addStretch()
        self.stack.addWidget(page)

    def init_otp_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Verification")
        title.setStyleSheet(QSS_STYLES.get("title_label", "font-size: 24px; font-weight: bold;"))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Enter the 6-digit code sent to your email.")
        subtitle.setStyleSheet(QSS_STYLES.get("subtitle_label", "font-size: 14px; color: #A0A0A0;"))
        subtitle.setAlignment(Qt.AlignCenter)
        self.input_otp = QLineEdit()
        self.input_otp.setPlaceholderText("XXXXXX")
        self.input_otp.setStyleSheet(QSS_STYLES.get("input_field", "padding: 10px;"))
        self.input_otp.setAlignment(Qt.AlignCenter)
        btn_verify = QPushButton("Verify Code")
        btn_verify.setCursor(Qt.PointingHandCursor)
        btn_verify.setStyleSheet(QSS_STYLES.get("login_button", "padding: 10px; background-color: #6200ea;"))
        btn_verify.clicked.connect(self.handle_verify_otp)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.input_otp)
        layout.addWidget(btn_verify)
        layout.addStretch()
        self.stack.addWidget(page)

    # --- UPDATED: RESET PAGE WITH EYE TOGGLES ---
    def init_reset_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("New Password")
        title.setStyleSheet(QSS_STYLES.get("title_label", "font-size: 24px; font-weight: bold;"))
        title.setAlignment(Qt.AlignCenter)

        self.input_new_pass = QLineEdit()
        self.input_new_pass.setPlaceholderText("New Password")
        self.input_new_pass.setEchoMode(QLineEdit.Password)
        self.input_new_pass.setStyleSheet(QSS_STYLES.get("input_field", "padding: 10px;"))

        # ADD TOGGLE 1
        self.add_password_toggle(self.input_new_pass)

        self.input_confirm_pass = QLineEdit()
        self.input_confirm_pass.setPlaceholderText("Confirm Password")
        self.input_confirm_pass.setEchoMode(QLineEdit.Password)
        self.input_confirm_pass.setStyleSheet(QSS_STYLES.get("input_field", "padding: 10px;"))

        # ADD TOGGLE 2
        self.add_password_toggle(self.input_confirm_pass)

        btn_submit = QPushButton("Change Password")
        btn_submit.setCursor(Qt.PointingHandCursor)
        btn_submit.setStyleSheet(QSS_STYLES.get("login_button", "padding: 10px; background-color: #6200ea;"))
        btn_submit.clicked.connect(self.handle_password_reset)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.input_new_pass)
        layout.addWidget(self.input_confirm_pass)
        layout.addWidget(btn_submit)
        layout.addStretch()
        self.stack.addWidget(page)

    # --- EYE TOGGLE HELPERS (Copy this anywhere you need it) ---
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

    # --- LOGIC FUNCTIONS (Unchanged) ---
    def check_email_in_db(self, email):
        conn = get_db_connection(self)
        if not conn: return None
        found_mail = None
        try:
            cursor = conn.cursor()
            query = "SELECT Email FROM Users WHERE Email = ?"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if row: found_mail = row[0]
        except Exception as e:
            print(f"Error checking table: {e}")
        conn.close()
        return found_mail

    def handle_send_otp(self):
        to_mail = self.input_email.text().strip()
        if "@" not in to_mail:
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return
        self.rec_email = self.check_email_in_db(to_mail)
        if not self.rec_email:
            QMessageBox.warning(self, "Error", "This email is not registered in our system.")
            return
        otp_code = send_otp_email(to_mail, subject="ESPORTIFY - Password Reset OTP")
        if otp_code:
            self.generated_otp = otp_code
            self.stack.setCurrentIndex(1)
        else:
            QMessageBox.critical(self, "Connection Error", "Failed to send email. Check your internet.")

    def handle_verify_otp(self):
        user_input = self.input_otp.text().strip()
        if user_input == self.generated_otp:
            QMessageBox.information(self, "Verified", "OTP Verified Successfully!")
            self.stack.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "Error", "Invalid OTP. Please check your email and try again.")

    def handle_password_reset(self):
        p1 = self.input_new_pass.text()
        p2 = self.input_confirm_pass.text()
        email = self.input_email.text().strip()
        if not p1 or p1 != p2:
            QMessageBox.warning(self, "Error", "Passwords do not match or field is empty.")
            return
        if len(p1) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters.")
            return
        conn = get_db_connection(self)
        if conn:
            try:
                cursor = conn.cursor()
                sql = "{CALL sp_ResetPassword (?, ?)}"
                params = (email, p1)
                cursor.execute(sql, params)
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Your password has been reset successfully.")
                self.close()
            except Exception as e:
                print(f"SQL Error: {e}")
                QMessageBox.critical(self, "Database Error", f"Failed to update password.\nError: {e}")