# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlayerWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 850)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        # --- SIDEBAR ---
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(260, 0))
        self.frame.setMaximumSize(QtCore.QSize(260, 16777215))
        self.frame.setObjectName("frame")

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(10, 30, 10, 20)
        self.verticalLayout_6.setSpacing(15)

        self.label = QtWidgets.QLabel("PLAYER")
        self.label.setMinimumHeight(80)
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_6.addWidget(self.label)

        self.verticalLayout_6.addItem(
            QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        def make_btn(text, name):
            btn = QtWidgets.QPushButton(text)
            btn.setObjectName(name)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.verticalLayout_6.addWidget(btn)
            return btn

        self.btn_find_tournaments = make_btn("Find Tournaments", "btn_find_tournaments")
        self.btn_my_tournaments = make_btn("My Tournaments", "btn_my_tournaments")
        self.btn_my_matches = make_btn("My Matches", "btn_my_matches")
        self.btn_file_dispute = make_btn("File Dispute", "btn_file_dispute")
        self.btn_edit_profile = make_btn("Edit Profile", "btn_edit_profile")

        self.verticalLayout_6.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.btn_logout = make_btn("Logout", "btn_logout")
        self.btn_logout.setMinimumHeight(50)

        self.horizontalLayout.addWidget(self.frame)

        # --- CONTENT AREA ---
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")

        def create_page(header_text, header_id):
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(40, 50, 40, 40)
            layout.setSpacing(20)
            lbl = QtWidgets.QLabel(header_text)
            lbl.setObjectName(header_id)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(lbl)
            return page, layout

        # 1. FIND PAGE
        self.page_find, self.layout_find = create_page("REGISTER FOR TOURNAMENTS", "view_tournnament_label")
        top_bar = QtWidgets.QHBoxLayout()
        self.input_search = QtWidgets.QLineEdit()
        self.input_search.setPlaceholderText("Search Game Name...")
        self.input_search.setFixedWidth(300)
        top_bar.addWidget(self.input_search)
        top_bar.addStretch()
        self.layout_find.addLayout(top_bar)

        self.table_find = QtWidgets.QTableWidget(0, 6)
        self.table_find.setHorizontalHeaderLabels(["ID", "Tournament Name", "Game", "Format", "Entry Fee", "Action"])
        self.table_find.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # --- FIX: MAKE READ ONLY ---
        self.table_find.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_find.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_find.addWidget(self.table_find)
        self.stackedWidget.addWidget(self.page_find)

        # 2. MY TOURNAMENTS
        self.page_my, self.layout_my = create_page("MY TOURNAMENTS", "view_tournnament_label")
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("Filter View:"))
        self.combo_filter = QtWidgets.QComboBox()
        self.combo_filter.addItems(["All Tournaments", "Participated", "Won", "Upcoming"])
        self.combo_filter.setFixedWidth(200)
        filter_layout.addWidget(self.combo_filter)
        filter_layout.addStretch()
        self.layout_my.addLayout(filter_layout)

        self.table_my = QtWidgets.QTableWidget(0, 6)
        self.table_my.setHorizontalHeaderLabels(["ID", "Tournament Name", "Game", "My Status", "Result", "Actions"])
        self.table_my.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_my.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        # --- FIX: MAKE READ ONLY ---
        self.table_my.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_my.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_my.addWidget(self.table_my)
        self.stackedWidget.addWidget(self.page_my)

        # 3. MY MATCHES
        self.page_matches, self.layout_matches = create_page("MY MATCH HISTORY", "header_matches")

        match_filter_layout = QtWidgets.QHBoxLayout()
        match_filter_layout.addWidget(QtWidgets.QLabel("Filter by Tournament:"))
        self.combo_match_filter = QtWidgets.QComboBox()
        self.combo_match_filter.addItems(["All Matches"])
        self.combo_match_filter.setFixedWidth(200)
        match_filter_layout.addWidget(self.combo_match_filter)
        match_filter_layout.addStretch()
        self.layout_matches.addLayout(match_filter_layout)

        self.lbl_matches_title = QtWidgets.QLabel("My Head-to-Head Record")
        self.lbl_matches_title.setStyleSheet("color: #bd93f9; font-size: 18px;")
        self.lbl_matches_title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout_matches.addWidget(self.lbl_matches_title)

        self.table_matches = QtWidgets.QTableWidget(0, 5)
        self.table_matches.setHorizontalHeaderLabels(["Tournament", "Round", "Opponent", "My Score", "Result"])
        self.table_matches.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # --- FIX: MAKE READ ONLY ---
        self.table_matches.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_matches.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_matches.addWidget(self.table_matches)

        self.btn_back_matches = QtWidgets.QPushButton("Back to My Tournaments")
        self.btn_back_matches.setObjectName("submit_create_tour_button")
        self.layout_matches.addWidget(self.btn_back_matches)

        self.stackedWidget.addWidget(self.page_matches)

        # 4. VIEW STANDINGS
        self.page_standings, self.layout_standings = create_page("TOURNAMENT STANDINGS", "header_standings")
        self.lbl_standings_title = QtWidgets.QLabel("Leaderboard")
        self.lbl_standings_title.setStyleSheet("color: #bd93f9; font-size: 18px;")
        self.lbl_standings_title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout_standings.addWidget(self.lbl_standings_title)

        self.table_standings = QtWidgets.QTableWidget(0, 3)
        self.table_standings.setHorizontalHeaderLabels(["Rank", "Player", "Score/Result"])
        self.table_standings.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # --- FIX: MAKE READ ONLY ---
        self.table_standings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_standings.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_standings.addWidget(self.table_standings)

        self.btn_back_standings = QtWidgets.QPushButton("Back to My Tournaments")
        self.btn_back_standings.setObjectName("submit_create_tour_button")
        self.layout_standings.addWidget(self.btn_back_standings)
        self.stackedWidget.addWidget(self.page_standings)

        # 5. FILE DISPUTE PAGE
        self.page_dispute, self.layout_dispute = create_page("FILE A DISPUTE", "header_cancel")

        self.card_dispute = QtWidgets.QFrame()
        self.card_dispute.setObjectName("frame_2")
        self.form_dispute = QtWidgets.QFormLayout(self.card_dispute)
        self.form_dispute.setContentsMargins(50, 50, 50, 50)
        self.form_dispute.setVerticalSpacing(20)

        self.input_dispute_player = QtWidgets.QLineEdit()
        self.input_dispute_player.setPlaceholderText("Gamertag of offending player")

        self.input_dispute_reason = QtWidgets.QTextEdit()
        self.input_dispute_reason.setPlaceholderText("Describe the incident...")
        self.input_dispute_reason.setMaximumHeight(100)
        self.input_dispute_reason.setStyleSheet(
            "background-color: #1a1a1d; border: 1px solid #333; border-radius: 6px; color: white; padding: 5px;")

        self.btn_submit_dispute = QtWidgets.QPushButton("Submit Report")
        self.btn_submit_dispute.setObjectName("submit_create_tour_button")
        self.btn_submit_dispute.setMinimumHeight(45)
        self.btn_submit_dispute.setStyleSheet(
            "background-color: #d32f2f; color: white; font-weight: bold; border-radius: 6px;")

        self.form_dispute.addRow("Report Player:", self.input_dispute_player)
        self.form_dispute.addRow("Reason:", self.input_dispute_reason)
        self.form_dispute.addRow(self.btn_submit_dispute)

        self.layout_dispute.addWidget(self.card_dispute)
        self.layout_dispute.addStretch()
        self.stackedWidget.addWidget(self.page_dispute)

        # 6. EDIT PROFILE (FIXED: Using self variables)
        self.page_profile, self.layout_prof = create_page("EDIT PLAYER PROFILE", "header_details")
        self.card_prof = QtWidgets.QFrame()
        self.card_prof.setObjectName("frame_2")
        self.form_prof = QtWidgets.QFormLayout(self.card_prof)
        self.form_prof.setContentsMargins(50, 50, 50, 50)
        self.form_prof.setVerticalSpacing(25)

        self.input_prof_gamertag = QtWidgets.QLineEdit()
        self.input_prof_email = QtWidgets.QLineEdit()
        self.input_prof_pass = QtWidgets.QLineEdit()
        self.input_prof_pass.setPlaceholderText("Enter current password to save changes")
        self.input_prof_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.input_prof_new_pass = QtWidgets.QLineEdit()
        self.input_prof_new_pass.setPlaceholderText("Optional: Enter new password")
        self.input_prof_new_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.form_prof.addRow("Gamertag:", self.input_prof_gamertag)
        self.form_prof.addRow("Email (Read-only):", self.input_prof_email)
        self.input_prof_email.setReadOnly(True)
        self.form_prof.addRow("Current Password:", self.input_prof_pass)
        self.form_prof.addRow("New Password:", self.input_prof_new_pass)

        self.btn_save_profile = QtWidgets.QPushButton("Update Profile")
        self.btn_save_profile.setObjectName("submit_create_tour_button")
        self.btn_save_profile.setMinimumHeight(45)
        self.form_prof.addRow(self.btn_save_profile)

        self.layout_prof.addWidget(self.card_prof)
        self.layout_prof.addStretch()
        self.stackedWidget.addWidget(self.page_profile)

        self.horizontalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)