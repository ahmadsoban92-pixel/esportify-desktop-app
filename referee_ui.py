# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RefereeWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        # ==================== SIDEBAR ====================
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(260, 0))
        self.frame.setMaximumSize(QtCore.QSize(260, 16777215))
        self.frame.setObjectName("frame")

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(10, 30, 10, 20)
        self.verticalLayout_6.setSpacing(15)

        self.label = QtWidgets.QLabel("REFEREE")
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

        self.btn_assigned = make_btn("Assigned Matches", "btn_assigned")
        self.btn_history = make_btn("Match History", "btn_history")
        self.btn_disputes = make_btn("Dispute Center", "btn_disputes")
        self.btn_profile = make_btn("Edit Profile", "btn_profile")

        self.verticalLayout_6.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.btn_logout = make_btn("Logout", "btn_logout")
        self.btn_logout.setMinimumHeight(50)

        self.horizontalLayout.addWidget(self.frame)

        # ==================== MAIN CONTENT ====================
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")

        # --- HELPER: PAGE BUILDER ---
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

        # 1. ASSIGNED MATCHES
        self.page_assigned, self.layout_assigned = create_page("ASSIGNED MATCHES", "view_tournnament_label")
        self.layout_assigned.addWidget(QtWidgets.QLabel("Select a match to enter the Score Room."))

        self.table_assigned = QtWidgets.QTableWidget(0, 5)
        self.table_assigned.setHorizontalHeaderLabels(["Match ID", "Game", "Type", "Status", "Action"])
        self.table_assigned.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- FIX: MAKE READ ONLY ---
        self.table_assigned.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_assigned.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_assigned.addWidget(self.table_assigned)
        self.stackedWidget.addWidget(self.page_assigned)

        # 2. SCORING ROOM: POINTS (Battle Royale)
        self.page_score_points, self.layout_score_pts = create_page("MATCH ROOM: POINTS", "header_edit")
        self.lbl_match_info_pts = QtWidgets.QLabel("Match: PUBG Finals | ID: 101")
        self.lbl_match_info_pts.setStyleSheet("font-size: 16px; color: #bd93f9; font-weight: bold;")
        self.layout_score_pts.addWidget(self.lbl_match_info_pts)

        self.table_points = QtWidgets.QTableWidget(0, 4)
        self.table_points.setHorizontalHeaderLabels(["Player Gamertag", "Kills (Pts)", "Placement", "Total Score"])
        self.table_points.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # NOTE: This table STAYS editable so Referees can type scores!

        self.layout_score_pts.addWidget(self.table_points)

        btn_box_pts = QtWidgets.QHBoxLayout()
        self.btn_back_pts = QtWidgets.QPushButton("Back to Matches")
        self.btn_back_pts.setFixedWidth(150)
        self.btn_back_pts.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
        btn_box_pts.addWidget(self.btn_back_pts)
        btn_box_pts.addStretch()
        self.btn_submit_pts = QtWidgets.QPushButton("Finalize Results")
        self.btn_submit_pts.setObjectName("submit_create_tour_button")
        self.btn_submit_pts.setFixedWidth(200)
        btn_box_pts.addWidget(self.btn_submit_pts)
        self.layout_score_pts.addLayout(btn_box_pts)
        self.stackedWidget.addWidget(self.page_score_points)

        # 3. SCORING ROOM: KNOCKOUT (1v1)
        self.page_score_ko, self.layout_score_ko = create_page("MATCH ROOM: VERSUS", "header_edit")
        self.card_ko = QtWidgets.QFrame()
        self.card_ko.setObjectName("frame_2")
        self.layout_ko_form = QtWidgets.QVBoxLayout(self.card_ko)
        self.layout_ko_form.setContentsMargins(50, 50, 50, 50)
        self.layout_ko_form.setSpacing(30)

        vs_layout = QtWidgets.QHBoxLayout()
        self.lbl_player_a = QtWidgets.QLabel("PLAYER 1")
        self.lbl_player_a.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.lbl_player_a.setAlignment(QtCore.Qt.AlignCenter)
        lbl_vs = QtWidgets.QLabel("VS")
        lbl_vs.setStyleSheet("color: #7b2cbf; font-size: 36px; font-weight: bold;")
        lbl_vs.setAlignment(QtCore.Qt.AlignCenter)
        lbl_vs.setFixedWidth(80)
        self.lbl_player_b = QtWidgets.QLabel("PLAYER 2")
        self.lbl_player_b.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.lbl_player_b.setAlignment(QtCore.Qt.AlignCenter)
        vs_layout.addWidget(self.lbl_player_a, 1)
        vs_layout.addWidget(lbl_vs, 0)
        vs_layout.addWidget(self.lbl_player_b, 1)
        self.layout_ko_form.addLayout(vs_layout)

        score_layout = QtWidgets.QHBoxLayout()
        self.input_score_a = QtWidgets.QSpinBox()
        self.input_score_a.setRange(0, 100)
        self.input_score_a.setMinimumHeight(60)
        self.input_score_a.setStyleSheet("font-size: 28px; font-weight: bold; padding-left: 20px;")
        self.input_score_b = QtWidgets.QSpinBox()
        self.input_score_b.setRange(0, 100)
        self.input_score_b.setMinimumHeight(60)
        self.input_score_b.setStyleSheet("font-size: 28px; font-weight: bold; padding-left: 20px;")
        score_layout.addWidget(self.input_score_a)
        score_layout.addSpacing(80)
        score_layout.addWidget(self.input_score_b)
        self.layout_ko_form.addLayout(score_layout)

        self.combo_winner = QtWidgets.QComboBox()
        self.combo_winner.addItems(["Select Winner...", "Player 1", "Player 2", "Draw"])
        self.combo_winner.setMinimumHeight(45)
        self.layout_ko_form.addWidget(QtWidgets.QLabel("Declare Winner:"))
        self.layout_ko_form.addWidget(self.combo_winner)

        btn_layout_ko = QtWidgets.QHBoxLayout()
        self.btn_back_ko = QtWidgets.QPushButton("Back")
        self.btn_back_ko.setFixedWidth(120)
        self.btn_back_ko.setMinimumHeight(45)
        self.btn_back_ko.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
        self.btn_submit_ko = QtWidgets.QPushButton("Submit Result")
        self.btn_submit_ko.setObjectName("submit_create_tour_button")
        self.btn_submit_ko.setMinimumHeight(45)
        btn_layout_ko.addWidget(self.btn_back_ko)
        btn_layout_ko.addSpacing(20)
        btn_layout_ko.addWidget(self.btn_submit_ko)
        self.layout_ko_form.addLayout(btn_layout_ko)
        self.layout_score_ko.addWidget(self.card_ko)
        self.layout_score_ko.addStretch()
        self.stackedWidget.addWidget(self.page_score_ko)

        # 4. MATCH HISTORY
        self.page_history, self.layout_hist = create_page("MATCH HISTORY", "header_report")
        self.table_history = QtWidgets.QTableWidget(0, 4)
        self.table_history.setHorizontalHeaderLabels(["Match ID", "Game", "Winner", "Date"])
        self.table_history.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- FIX: MAKE READ ONLY ---
        self.table_history.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_history.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_hist.addWidget(self.table_history)
        self.stackedWidget.addWidget(self.page_history)

        # 5. DISPUTE CENTER
        self.page_disputes, self.layout_disp = create_page("DISPUTE CENTER", "header_cancel")
        self.table_disputes = QtWidgets.QTableWidget(0, 4)
        self.table_disputes.setHorizontalHeaderLabels(["Match ID", "Reported By", "Reason", "Action"])
        self.table_disputes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- FIX: MAKE READ ONLY ---
        self.table_disputes.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_disputes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.layout_disp.addWidget(self.table_disputes)
        self.stackedWidget.addWidget(self.page_disputes)

        # 6. PROFILE
        self.page_profile, self.layout_prof = create_page("EDIT PROFILE", "header_details")
        self.card_prof = QtWidgets.QFrame()
        self.card_prof.setObjectName("frame_2")
        self.form_prof = QtWidgets.QFormLayout(self.card_prof)
        self.form_prof.setContentsMargins(50, 50, 50, 50)
        self.form_prof.setVerticalSpacing(20)

        # --- DEFINED VARIABLES WITH 'self.' ---
        self.input_prof_name = QtWidgets.QLineEdit()
        self.input_prof_email = QtWidgets.QLineEdit()

        self.input_prof_pass = QtWidgets.QLineEdit()
        self.input_prof_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_prof_pass.setPlaceholderText("Current Password")

        self.input_prof_new_pass = QtWidgets.QLineEdit()
        self.input_prof_new_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_prof_new_pass.setPlaceholderText("New Password (Optional)")

        self.btn_save_profile = QtWidgets.QPushButton("Save Changes")
        self.btn_save_profile.setObjectName("submit_create_tour_button")
        self.btn_save_profile.setMinimumHeight(45)

        self.form_prof.addRow("Full Name:", self.input_prof_name)
        self.form_prof.addRow("Email:", self.input_prof_email)
        self.form_prof.addRow("Current Password:", self.input_prof_pass)
        self.form_prof.addRow("New Password:", self.input_prof_new_pass)
        self.form_prof.addRow(self.btn_save_profile)

        self.layout_prof.addWidget(self.card_prof)
        self.layout_prof.addStretch()
        self.stackedWidget.addWidget(self.page_profile)

        self.horizontalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)