import sys
import re  # <--- Required for Regex Validation
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from styles import QSS_STYLES
from connection import get_db_connection  # <--- Helper Import


class RefereeRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apply for Referee")
        self.setFixedSize(450, 700)
        self.setStyleSheet(
            QSS_STYLES.get("window_background", "background-color: #0f0b12; color: white; font-family: Segoe UI;"))

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(10)

        # --- HEADER ---
        self.lbl_title = QLabel("BECOME A REFEREE")
        self.lbl_title.setStyleSheet(QSS_STYLES["logo_label"])
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Join the team and manage tournaments")
        self.lbl_subtitle.setStyleSheet("color: #a0a0a0; font-size: 13px; margin-bottom: 10px;")
        self.lbl_subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_subtitle)

        # --- FORM INPUTS ---
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)

        # 1. Full Name
        self.lbl_name = QLabel("Full Name:")
        self.lbl_name.setStyleSheet(QSS_STYLES["standard_label"])
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("John Doe")
        self.input_name.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_name)
        self.form_layout.addWidget(self.input_name)

        # 2. Email
        self.lbl_email = QLabel("Email Address:")
        self.lbl_email.setStyleSheet(QSS_STYLES["standard_label"])
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("referee@gmail.com")
        self.input_email.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_email)
        self.form_layout.addWidget(self.input_email)

        # 3. CNIC
        self.lbl_cnic = QLabel("CNIC:")
        self.lbl_cnic.setStyleSheet(QSS_STYLES["standard_label"])
        self.input_cnic = QLineEdit()
        self.input_cnic.setPlaceholderText("35202-1234567-8")
        self.input_cnic.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_cnic)
        self.form_layout.addWidget(self.input_cnic)

        # 4. Game Specialization (DYNAMIC)
        self.lbl_game = QLabel("Game Specialization:")
        self.lbl_game.setStyleSheet(QSS_STYLES["standard_label"])
        self.combo_game = QComboBox()
        self.combo_game.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_game)
        self.form_layout.addWidget(self.combo_game)

        # 5. Experience
        self.lbl_exp = QLabel("Years of Experience:")
        self.lbl_exp.setStyleSheet(QSS_STYLES["standard_label"])
        self.input_exp = QLineEdit()
        self.input_exp.setPlaceholderText("e.g. 2")
        self.input_exp.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_exp)
        self.form_layout.addWidget(self.input_exp)

        # 6. Password
        self.lbl_pass = QLabel("Set Password:")
        self.lbl_pass.setStyleSheet(QSS_STYLES["standard_label"])
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setStyleSheet(QSS_STYLES["input_field"])
        self.form_layout.addWidget(self.lbl_pass)
        self.form_layout.addWidget(self.input_pass)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # --- SUBMIT BUTTON ---
        self.btn_submit = QPushButton("SUBMIT APPLICATION")
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.setStyleSheet(QSS_STYLES["login_button"])
        self.btn_submit.clicked.connect(self.handle_application)
        self.layout.addWidget(self.btn_submit)

        # --- LOAD DATA (Runs immediately) ---
        self.load_games_from_db()

    # --- FUNCTION 1: Fetch Games from DB ---
    def load_games_from_db(self):
        """Fetches game names from SQL Server and fills the ComboBox"""
        self.combo_game.clear()
        self.combo_game.addItem("Select Game...")

        conn = get_db_connection(self)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM g_names")

                rows = cursor.fetchall()
                for row in rows:
                    self.combo_game.addItem(row.g_name)

                conn.close()
            except Exception as e:
                print(f"Failed to load games: {e}")

    # --- FUNCTION 2: Submit with Regex Validation ---
    def handle_application(self):
        # 1. Gather Inputs
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        cnic = self.input_cnic.text().strip()
        game = self.combo_game.currentText()
        pwd = self.input_pass.text()
        exp_text = self.input_exp.text().strip()

        # --- VALIDATION (REGEX) ---

        # A. Empty Check
        if not name or not email or not cnic or not pwd or not exp_text or game == "Select Game...":
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return

        # B. Name Check (Letters & Spaces only)
        if not re.match(r"^[A-Za-z ]+$", name):
            QMessageBox.warning(self, "Invalid Name", "Name can only contain letters and spaces.")
            return

        # C. Email Check (Strict: @gmail.com ONLY, no dots in username)
        if not re.match(r"^[a-zA-Z0-9_]+@gmail\.com$", email):
            QMessageBox.warning(self, "Invalid Email", "Only @gmail.com allowed.\n(No dots allowed in username).")
            return

        # D. CNIC Check (Format: 12345-1234567-1)
        if not re.match(r"^\d{5}-\d{7}-\d{1}$", cnic):
            QMessageBox.warning(self, "Invalid CNIC", "CNIC must follow the format:\n12345-1234567-1")
            return

        # E. Password Check
        if len(pwd) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long.")
            return

        # F. Experience Check
        if not exp_text.isdigit():
            QMessageBox.warning(self, "Input Error", "Experience must be a positive number.")
            return

        experience = int(exp_text)

        # --- DATABASE SUBMISSION ---
        conn = get_db_connection(self)
        if conn:
            try:
                cursor = conn.cursor()

                # Call Stored Procedure
                sql_command = "{CALL sp_RegisterReferee (?, ?, ?, ?, ?, ?)}"
                parameters = (name, email, pwd, cnic, experience, game)

                cursor.execute(sql_command, parameters)

                # Read Result
                row = cursor.fetchone()

                if row:
                    if row.Result == 1:
                        QMessageBox.information(self, "Success", row.Message)
                        self.close()
                    else:
                        QMessageBox.warning(self, "Registration Failed", row.Message)

                conn.commit()
                conn.close()

            except Exception as e:
                # Handle SQL Errors (e.g., Duplicate Email)
                error_str = str(e)
                if "Violation of UNIQUE KEY constraint" in error_str:
                    QMessageBox.warning(self, "Error", "This Email or CNIC is already registered.")
                else:
                    QMessageBox.critical(self, "Database Error", f"Transaction failed.\nError: {e}")