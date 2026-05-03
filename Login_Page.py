from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(QtCore.QSize(500, 700))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.masterLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.masterLayout.setAlignment(QtCore.Qt.AlignCenter)

        # --- CONTENT CARD ---
        self.content_container = QtWidgets.QWidget(self.centralwidget)
        self.content_container.setObjectName("content_container")
        self.content_container.setFixedWidth(400)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.content_container)
        self.verticalLayout.setSpacing(15)

        # Labels
        self.Esportify_Label = QtWidgets.QLabel("ESPORTIFY")
        self.Esportify_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Esportify_Label.setObjectName("Esportify_Label")
        self.verticalLayout.addWidget(self.Esportify_Label)

        self.Login_Label = QtWidgets.QLabel("LOGIN")
        self.Login_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Login_Label.setObjectName("Login_Label")
        self.verticalLayout.addWidget(self.Login_Label)

        self.credentials_label = QtWidgets.QLabel("Enter credentials to access account")
        self.credentials_label.setAlignment(QtCore.Qt.AlignCenter)
        self.credentials_label.setObjectName("credentials_label")
        self.verticalLayout.addWidget(self.credentials_label)

        # Inputs
        self.Email_Label = QtWidgets.QLabel("Email Address:")
        self.verticalLayout.addWidget(self.Email_Label)
        self.Input_Email = QtWidgets.QLineEdit()
        self.Input_Email.setObjectName("Input_Email")
        self.verticalLayout.addWidget(self.Input_Email)

        self.Password_Label = QtWidgets.QLabel("Password:")
        self.verticalLayout.addWidget(self.Password_Label)

        self.Input_Password = QtWidgets.QLineEdit()
        self.Input_Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Input_Password.setObjectName("Input_Password")
        self.verticalLayout.addWidget(self.Input_Password)

        # --- ADD EYE TOGGLE HERE ---
        self.add_password_toggle(self.Input_Password)

        # Forgot Pass
        self.ForgotPass_Button = QtWidgets.QPushButton("Forgot Password?")
        self.ForgotPass_Button.setCursor(QtCore.Qt.PointingHandCursor)
        self.ForgotPass_Button.setObjectName("ForgotPass_Button")
        self.verticalLayout.addWidget(self.ForgotPass_Button, 0, QtCore.Qt.AlignRight)

        # Radio Buttons
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.Radio_Admin = QtWidgets.QRadioButton("Admin")
        self.Radio_Referee = QtWidgets.QRadioButton("Referee")
        self.Radio_Player = QtWidgets.QRadioButton("Player")
        self.Radio_Player.setChecked(True)

        self.radio_layout.addWidget(self.Radio_Admin)
        self.radio_layout.addWidget(self.Radio_Referee)
        self.radio_layout.addWidget(self.Radio_Player)
        self.verticalLayout.addLayout(self.radio_layout)

        # Buttons
        self.Login_Button = QtWidgets.QPushButton("LOGIN")
        self.Login_Button.setObjectName("Login_Button")
        self.verticalLayout.addWidget(self.Login_Button)

        self.CreateAcc_Button = QtWidgets.QPushButton("Create Player Account")
        self.CreateAcc_Button.setObjectName("CreateAcc_Button")
        self.verticalLayout.addWidget(self.CreateAcc_Button)

        # Split Buttons
        self.split_layout = QtWidgets.QHBoxLayout()
        self.ApplyRef_Button = QtWidgets.QPushButton("Apply Referee")
        self.ApplyRef_Button.setObjectName("ApplyRef_Button")
        self.split_layout.addWidget(self.ApplyRef_Button)
        self.verticalLayout.addLayout(self.split_layout)

        self.masterLayout.addWidget(self.content_container)
        MainWindow.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # --- HELPER: EYE TOGGLE LOGIC ---
    def add_password_toggle(self, line_edit):
        """Adds a clickable eye icon to the right side of the password field"""
        # Create Action
        action = line_edit.addAction(self.get_eye_icon(False), QtWidgets.QLineEdit.TrailingPosition)
        action.setToolTip("Show Password")

        # Connect Trigger
        action.triggered.connect(lambda: self.toggle_password_visibility(line_edit, action))

    def toggle_password_visibility(self, line_edit, action):
        if line_edit.echoMode() == QtWidgets.QLineEdit.Password:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Normal)
            action.setIcon(self.get_eye_icon(True))  # Open Eye
        else:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
            action.setIcon(self.get_eye_icon(False))  # Closed Eye

    def get_eye_icon(self, is_open):
        """Draws a simple Eye icon dynamically so you don't need image files"""
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)

        # Set text color based on open/close
        if is_open:
            painter.setPen(QtGui.QColor("#4caf50"))  # Green for open
            text = "O"  # Simple representation
        else:
            painter.setPen(QtGui.QColor("#a0a0a0"))  # Grey for closed
            text = "Ø"  # Simple representation

        font = QtGui.QFont("Arial", 14, QtGui.QFont.Bold)
        painter.setFont(font)
        painter.drawText(QtCore.QRect(0, 0, 24, 24), QtCore.Qt.AlignCenter, text)
        painter.end()
        return QtGui.QIcon(pixmap)