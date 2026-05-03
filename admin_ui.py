# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 850)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        # ==================== SIDEBAR ====================
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(260, 0))
        self.frame.setMaximumSize(QtCore.QSize(260, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(10, 30, 10, 20)
        self.verticalLayout_6.setSpacing(15)

        self.label = QtWidgets.QLabel("ADMIN")
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

        self.btn_create_tournament = make_btn("Create Tournaments", "btn_create_tournament")
        self.btn_cancel_tournaments = make_btn("Cancel Tournaments", "btn_cancel_tournaments")
        self.btn_view_tournaments = make_btn("View Tournaments", "btn_view_tournaments")
        self.btn_edit_tournaments = make_btn("Edit Tournaments", "btn_edit_tournaments")
        self.btn_approve_payments = make_btn("Approve Payments", "btn_approve_payments")
        self.btn_manage_referees = make_btn("Manage Referees", "btn_manage_referees")
        self.btn_manage_players = make_btn("Manage Players", "btn_manage_players")
        self.btn_edit_games = make_btn("Edit Games", "btn_edit_games")
        # CHANGED: Button Name
        self.btn_system_history = make_btn("System History", "btn_edit_details")

        self.verticalLayout_6.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.btn_logout = make_btn("Logout", "btn_logout")
        self.btn_logout.setMinimumHeight(50)

        self.horizontalLayout.addWidget(self.frame)

        # ==================== MAIN CONTENT ====================
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

        # 1. CREATE TOURNAMENT
        self.page_create_tournament = QtWidgets.QWidget()
        self.page_create_tournament.setObjectName("page_create_tournament")
        self.layout_create_page = QtWidgets.QVBoxLayout(self.page_create_tournament)
        self.layout_create_page.setContentsMargins(0, 0, 0, 0)

        self.scroll_create = QtWidgets.QScrollArea()
        self.scroll_create.setWidgetResizable(True)
        self.scroll_create.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content_create = QtWidgets.QWidget()

        self.vbox_create = QtWidgets.QVBoxLayout(self.content_create)
        self.vbox_create.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.vbox_create.setContentsMargins(40, 50, 40, 40)
        self.vbox_create.setSpacing(20)

        self.header_create = QtWidgets.QLabel("CREATE TOURNAMENT")
        self.header_create.setObjectName("create_tournament_label")
        self.header_create.setAlignment(QtCore.Qt.AlignCenter)
        self.vbox_create.addWidget(self.header_create)

        self.card_create = QtWidgets.QFrame()
        self.card_create.setObjectName("frame_2")
        self.card_create.setFixedWidth(800)
        self.form_create = QtWidgets.QFormLayout(self.card_create)
        self.form_create.setContentsMargins(50, 50, 50, 50)
        self.form_create.setVerticalSpacing(25)

        self.input_tour_name = QtWidgets.QLineEdit()
        self.input_tour_game = QtWidgets.QComboBox()
        self.input_tour_format = QtWidgets.QComboBox()
        self.input_tour_format.addItems(["Knockout", "Battle Royale"])
        # FIX 1: Make Format Read-Only
        self.input_tour_format.setEnabled(False)

        self.input_tour_venue = QtWidgets.QLineEdit()
        self.input_tour_fee = QtWidgets.QLineEdit()
        self.input_tour_start = QtWidgets.QDateEdit()
        self.input_tour_start.setCalendarPopup(True)
        self.input_tour_start.setDate(QtCore.QDate.currentDate())
        self.input_tour_end = QtWidgets.QDateEdit()
        self.input_tour_end.setCalendarPopup(True)
        self.input_tour_end.setDate(QtCore.QDate.currentDate())

        self.form_create.addRow(QtWidgets.QLabel("Tournament Name:"), self.input_tour_name)
        self.form_create.addRow(QtWidgets.QLabel("Select Game:"), self.input_tour_game)
        self.form_create.addRow(QtWidgets.QLabel("Format (Auto):"), self.input_tour_format)
        self.form_create.addRow(QtWidgets.QLabel("Select Venue:"), self.input_tour_venue)

        self.input_tour_players = QtWidgets.QComboBox()
        self.input_tour_players.addItems(["8", "16", "32"])

        self.form_create.addRow(QtWidgets.QLabel("Select Players:"), self.input_tour_players)
        self.form_create.addRow(QtWidgets.QLabel("Entry Fee:"), self.input_tour_fee)
        self.form_create.addRow(QtWidgets.QLabel("Start Date:"), self.input_tour_start)
        self.form_create.addRow(QtWidgets.QLabel("End Date:"), self.input_tour_end)

        self.btn_submit_tour = QtWidgets.QPushButton("Submit")
        self.btn_submit_tour.setMinimumHeight(45)
        self.btn_submit_tour.setObjectName("submit_create_tour_button")
        self.form_create.addRow(self.btn_submit_tour)

        self.vbox_create.addWidget(self.card_create)
        self.scroll_create.setWidget(self.content_create)
        self.layout_create_page.addWidget(self.scroll_create)
        self.stackedWidget.addWidget(self.page_create_tournament)

        # 2. VIEW TOURNAMENTS
        self.page_view_tournaments, self.layout_view = create_page("TOURNAMENT INVENTORY", "view_tournnament_label")
        top_bar_view = QtWidgets.QHBoxLayout()
        self.search_view = QtWidgets.QLineEdit()
        self.search_view.setPlaceholderText("Search by Game Name...")
        self.search_view.setFixedWidth(300)
        top_bar_view.addWidget(self.search_view)
        top_bar_view.addStretch()
        self.layout_view.addLayout(top_bar_view)
        self.table_view = QtWidgets.QTableWidget(0, 6)
        self.table_view.setHorizontalHeaderLabels(["ID", "Name", "Game", "Format", "Status", "Action"])
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_view.addWidget(self.table_view)
        self.stackedWidget.addWidget(self.page_view_tournaments)

        # 3. EDIT TOURNAMENTS (ENTRY FEE)
        self.page_edit_tournaments, self.layout_edit = create_page("EDIT TOURNAMENTS (ENTRY FEE)", "header_edit")
        self.table_edit = QtWidgets.QTableWidget(0, 4)
        self.table_edit.setHorizontalHeaderLabels(["ID", "Name", "Current Fee", "Action"])
        self.table_edit.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_edit.addWidget(self.table_edit)
        self.stackedWidget.addWidget(self.page_edit_tournaments)

        # 3a. POINTS TABLE
        self.page_points_table, self.layout_points = create_page("POINTS TABLE", "header_edit")
        self.table_points = QtWidgets.QTableWidget(0, 2)
        self.table_points.setHorizontalHeaderLabels(["Player Name", "Total Points"])
        self.table_points.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_points.addWidget(self.table_points)
        self.stackedWidget.addWidget(self.page_points_table)

        # 3b. BRACKETS
        self.page_brackets, self.layout_bracket = create_page("TOURNAMENT BRACKET", "header_edit")
        self.bracket_area = QtWidgets.QScrollArea()
        self.bracket_content = QtWidgets.QWidget()
        self.bracket_grid = QtWidgets.QGridLayout(self.bracket_content)
        self.bracket_area.setWidget(self.bracket_content)
        self.bracket_area.setWidgetResizable(True)
        self.layout_bracket.addWidget(self.bracket_area)
        self.stackedWidget.addWidget(self.page_brackets)

        # 4. CANCEL TOURNAMENTS
        self.page_cancel_tournaments, self.layout_cancel = create_page("CANCEL TOURNAMENTS", "header_cancel")
        self.table_cancel = QtWidgets.QTableWidget(0, 4)
        self.table_cancel.setHorizontalHeaderLabels(["ID", "Name", "Start Date", "Action"])
        self.table_cancel.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_cancel.addWidget(self.table_cancel)
        self.stackedWidget.addWidget(self.page_cancel_tournaments)

        # 5. MANAGE REFEREES
        self.page_manage_referees, self.layout_ref = create_page("MANAGE REFEREES", "header_referee")
        self.layout_ref.addWidget(QtWidgets.QLabel("PENDING APPROVALS"))
        self.table_ref_requests = QtWidgets.QTableWidget(0, 3)
        self.table_ref_requests.setHorizontalHeaderLabels(["Name", "Specialization", "Action"])
        self.table_ref_requests.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_ref.addWidget(self.table_ref_requests)

        self.layout_ref.addWidget(QtWidgets.QLabel("CURRENT REFEREES"))
        self.table_ref_current = QtWidgets.QTableWidget(0, 3)
        self.table_ref_current.setHorizontalHeaderLabels(["ID", "Name", "Action"])
        self.table_ref_current.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_ref.addWidget(self.table_ref_current)
        self.stackedWidget.addWidget(self.page_manage_referees)

        # 6. APPROVE PAYMENTS
        self.page_approve_payments, self.layout_pay = create_page("APPROVE PAYMENTS", "header_payment")
        self.table_pay = QtWidgets.QTableWidget(0, 5)
        self.table_pay.setHorizontalHeaderLabels(["Trans ID", "User", "Tournament", "Amount", "Action"])
        self.table_pay.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_pay.addWidget(self.table_pay)
        self.stackedWidget.addWidget(self.page_approve_payments)

        # 7. MANAGE PLAYERS
        self.page_manage_players, self.layout_players = create_page("MANAGE PLAYERS", "header_report")
        self.table_players = QtWidgets.QTableWidget(0, 4)
        self.table_players.setHorizontalHeaderLabels(["ID", "Gamertag", "Email", "Action"])
        self.table_players.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_players.addWidget(self.table_players)
        self.stackedWidget.addWidget(self.page_manage_players)

        # 8. EDIT GAMES
        self.page_edit_games, self.layout_games = create_page("EDIT GAMES", "header_details")
        game_form_layout = QtWidgets.QHBoxLayout()
        self.input_game_name = QtWidgets.QLineEdit()
        self.input_game_name.setPlaceholderText("Enter New Game Name")
        self.input_game_format = QtWidgets.QComboBox()
        self.input_game_format.addItems(["Knockout", "Battle Royale"])
        self.input_game_format.setFixedWidth(150)
        self.btn_add_game = QtWidgets.QPushButton("Add Game")
        self.btn_add_game.setObjectName("submit_create_tour_button")
        self.btn_add_game.setFixedWidth(120)

        game_form_layout.addWidget(self.input_game_name)
        game_form_layout.addWidget(self.input_game_format)
        game_form_layout.addWidget(self.btn_add_game)
        self.layout_games.addLayout(game_form_layout)

        self.table_games = QtWidgets.QTableWidget(0, 3)
        self.table_games.setHorizontalHeaderLabels(["Game Name", "Format", "Action"])
        self.table_games.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_games.addWidget(self.table_games)
        self.stackedWidget.addWidget(self.page_edit_games)

        # 9. SYSTEM HISTORY (REPLACED EDIT DETAILS)
        self.page_history, self.layout_history = create_page("SYSTEM HISTORY LOG", "header_details")

        self.table_history = QtWidgets.QTableWidget(0, 5)
        self.table_history.setHorizontalHeaderLabels(["User", "Entity", "ID", "Action", "Timestamp"])
        self.table_history.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layout_history.addWidget(self.table_history)

        btn_refresh_hist = QtWidgets.QPushButton("Refresh Log")
        btn_refresh_hist.setObjectName("submit_create_tour_button")
        self.layout_history.addWidget(btn_refresh_hist)
        self.btn_refresh_history = btn_refresh_hist  # for main file connection

        self.stackedWidget.addWidget(self.page_history)

        self.horizontalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Admin Dashboard"))