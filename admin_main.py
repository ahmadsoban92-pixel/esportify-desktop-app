import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QPushButton, QWidget, QHBoxLayout, QMessageBox, QAbstractItemView, \
    QInputDialog, QVBoxLayout, QHeaderView
from PyQt5.QtCore import pyqtSignal, QDate
import style1
from admin_ui import Ui_MainWindow
from connection import get_db_connection


class AdminDashboard(QtWidgets.QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user_email):
        super(AdminDashboard, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if hasattr(style1, 'stylesheet'):
            self.setStyleSheet(style1.stylesheet)

        self.current_admin_email = user_email
        print(f"DEBUG: Admin Dashboard loaded for {self.current_admin_email}")

        # Navigation Setup
        self.nav_map = [
            (self.ui.btn_create_tournament, self.ui.page_create_tournament),
            (self.ui.btn_view_tournaments, self.ui.page_view_tournaments),
            (self.ui.btn_edit_tournaments, self.ui.page_edit_tournaments),
            (self.ui.btn_cancel_tournaments, self.ui.page_cancel_tournaments),
            (self.ui.btn_manage_referees, self.ui.page_manage_referees),
            (self.ui.btn_approve_payments, self.ui.page_approve_payments),
            (self.ui.btn_manage_players, self.ui.page_manage_players),
            (self.ui.btn_edit_games, self.ui.page_edit_games),
            (self.ui.btn_system_history, self.ui.page_history),
        ]

        for btn, page in self.nav_map:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, p=page: self.refresh_page_data(p))

        self.ui.btn_logout.clicked.connect(self.perform_logout)

        # Connect Logic Buttons
        self.ui.btn_submit_tour.clicked.connect(self.submit_create_tournament)
        self.ui.btn_add_game.clicked.connect(self.submit_add_game)
        self.ui.btn_refresh_history.clicked.connect(self.load_system_history)

        # --- CRITICAL: MAKE ALL TABLES READ-ONLY ---
        self.apply_read_only_to_all_tables()

        # Initial Load
        self.refresh_page_data(self.ui.page_view_tournaments)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_view_tournaments)
        self.ui.btn_view_tournaments.setChecked(True)

    def perform_logout(self):
        self.logout_signal.emit()
        self.close()

    # --- CORE TABLE HELPER: MAKE READ-ONLY ---
    def apply_read_only_to_all_tables(self):
        table_names = [name for name in dir(self.ui) if
                       name.startswith('table_') and isinstance(getattr(self.ui, name), QtWidgets.QTableWidget)]

        for name in table_names:
            table_widget = getattr(self.ui, name)
            table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
            table_widget.setSelectionMode(QAbstractItemView.NoSelection)

    # --- DB HELPER ---
    def run_query(self, query, params=(), fetch=True):
        conn = get_db_connection()
        if not conn:
            QMessageBox.critical(self, "DB Error", "Failed to connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall() if fetch else None
            conn.commit()
            conn.close()
            return data if fetch else True
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
                conn.close()
            print(f"DB Error: {e}")
            QMessageBox.critical(self, "DB Operation Failed", f"An error occurred: {e}")
            return None

    def refresh_page_data(self, page_widget):
        self.ui.stackedWidget.setCurrentWidget(page_widget)

        if page_widget == self.ui.page_view_tournaments:
            self.load_view_tournaments()
        elif page_widget == self.ui.page_create_tournament:
            self.init_create_tournament_page()
        elif page_widget == self.ui.page_edit_tournaments:
            self.load_edit_tournaments()
        elif page_widget == self.ui.page_cancel_tournaments:
            self.load_cancel_tournaments()
        elif page_widget == self.ui.page_manage_referees:
            self.load_referees()
        elif page_widget == self.ui.page_approve_payments:
            self.load_payments()
        elif page_widget == self.ui.page_manage_players:
            self.load_players()
        elif page_widget == self.ui.page_edit_games:
            self.load_games()
        elif page_widget == self.ui.page_history:
            self.load_system_history()

    # ----------------------------------------------------
    # --- 1. CREATE TOURNAMENT LOGIC
    # ----------------------------------------------------
    def init_create_tournament_page(self):
        self.ui.input_tour_game.clear()
        self.ui.input_tour_game.addItem("Select Game...")
        rows = self.run_query("SELECT g_name, format FROM vw_GameDetails ORDER BY g_name")

        self.game_format_map = {}
        if rows:
            for name, fmt in rows:
                self.ui.input_tour_game.addItem(name)
                self.game_format_map[name] = fmt

        try:
            self.ui.input_tour_game.currentIndexChanged.disconnect()
        except Exception:
            pass
        self.ui.input_tour_game.currentIndexChanged.connect(self.update_tournament_format_label)

        self.update_tournament_format_label()

    def update_tournament_format_label(self):
        selected_game = self.ui.input_tour_game.currentText()
        format_text = self.game_format_map.get(selected_game, "N/A")
        self.ui.input_tour_format.setCurrentText(format_text)

    def submit_create_tournament(self):
        name = self.ui.input_tour_name.text().strip()
        game = self.ui.input_tour_game.currentText()
        fmt = self.ui.input_tour_format.currentText()
        venue = self.ui.input_tour_venue.text().strip()
        fee_text = self.ui.input_tour_fee.text().strip()
        players_text = self.ui.input_tour_players.currentText()

        start_date = self.ui.input_tour_start.date().toString("yyyy-MM-dd")
        end_date = self.ui.input_tour_end.date().toString("yyyy-MM-dd")

        if not name or not venue or not fee_text:
            QMessageBox.warning(self, "Missing Data", "Please fill in all fields.")
            return

        try:
            fee = int(fee_text)
            max_players = int(players_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Fee must be a number.")
            return

        query = "{CALL sp_CreateTournament (?, ?, ?, ?, ?, ?, ?, ?)}"
        params = (name, game, fmt, fee, max_players, start_date, end_date, venue)

        success = self.run_query(query, params, fetch=False)

        if success:
            QMessageBox.information(self, "Success", "Tournament Created Successfully!")
            self.ui.input_tour_name.clear()
            self.ui.input_tour_venue.clear()
            self.ui.input_tour_fee.clear()
            self.refresh_page_data(self.ui.page_view_tournaments)
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_view_tournaments)

    # ----------------------------------------------------
    # --- 2. EDIT GAMES LOGIC
    # ----------------------------------------------------
    def submit_add_game(self):
        game_name = self.ui.input_game_name.text().strip()
        game_format = self.ui.input_game_format.currentText()

        if not game_name:
            QMessageBox.warning(self, "Missing Data", "Please enter a game name.")
            return

        query = "{CALL sp_AddGame (?, ?)}"
        params = (game_name, game_format)

        result_rows = self.run_query(query, params, fetch=True)

        if result_rows:
            result_code = result_rows[0][0]
            message = result_rows[0][1]

            if result_code == 1:
                QMessageBox.information(self, "Success", message)
                self.ui.input_game_name.clear()
                self.load_games()
            else:
                QMessageBox.warning(self, "Failed to Add Game", message)
        else:
            QMessageBox.critical(self, "DB Error", "Failed to receive a response.")

    def load_games(self):
        rows = self.run_query("SELECT g_id, g_name, format FROM vw_GameDetails ORDER BY g_id")

        self.ui.table_games.setRowCount(0)
        if not rows: return

        self.ui.table_games.setRowCount(len(rows))

        for r, row in enumerate(rows):
            game_id, name, fmt = row
            self.ui.table_games.setItem(r, 0, QTableWidgetItem(name))
            self.ui.table_games.setItem(r, 1, QTableWidgetItem(fmt))
            self.add_action_buttons(
                self.ui.table_games, r, 2,
                [{"text": "Delete", "color": "#d32f2f", "action": ("delete_game", game_id, None)}]
            )

    # --- BUTTON RENDERER ---
    def add_action_buttons(self, table, row, col, buttons_config):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        for btn_conf in buttons_config:
            btn = QPushButton(btn_conf["text"])
            btn.setStyleSheet(f"background-color: {btn_conf['color']}; color: white; border-radius: 4px; padding: 4px;")
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

            action_data = btn_conf["action"]
            btn.clicked.connect(lambda checked, data=action_data: self.perform_table_action(table, data))

            layout.addWidget(btn)

        layout.addStretch()
        table.setCellWidget(row, col, container)

    def show_image_dialog(self, image_data):
        # Create a Dialog Window
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Payment Proof")
        dialog.setMinimumSize(600, 600)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Create Label to hold Image
        lbl_image = QtWidgets.QLabel()
        lbl_image.setAlignment(QtCore.Qt.AlignCenter)

        # Load Pixmap from Binary Data
        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(image_data):
            # Scale image to fit dialog
            lbl_image.setPixmap(pixmap.scaled(550, 550, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_image.setText("Error loading image format.")

        layout.addWidget(lbl_image)

        btn_close = QtWidgets.QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        dialog.exec_()

    def show_referee_assignments_dialog(self, tournament_id):
        # 1. Fetch Data
        query = """
            SELECT m.m_id, m.round_num, u.name, m.status 
            FROM Match m
            JOIN Users u ON m.r_id = u.u_id
            WHERE m.t_id = ?
            ORDER BY m.round_num, m.m_id
        """
        rows = self.run_query(query, (tournament_id,))

        # 2. Create Dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Referee Assignments (Tournament {tournament_id})")
        dialog.setMinimumSize(600, 400)
        layout = QtWidgets.QVBoxLayout(dialog)

        # 3. Create Table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Match ID", "Round", "Referee Name", "Match Status"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        if rows:
            table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                table.setItem(r, 0, QTableWidgetItem(str(row[0])))
                table.setItem(r, 1, QTableWidgetItem(str(row[1])))
                table.setItem(r, 2, QTableWidgetItem(str(row[2])))
                table.setItem(r, 3, QTableWidgetItem(str(row[3])))
        else:
            QtWidgets.QMessageBox.information(dialog, "Info", "No matches generated for this tournament yet.")

        layout.addWidget(table)
        btn_close = QtWidgets.QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        dialog.exec_()

    # --- MAIN ACTION HANDLER ---
    def perform_table_action(self, table, action_data):
        action_type, target_id, extra = action_data
        success = False

        if action_type == "delete_game":
            confirm = QMessageBox.question(self, "Confirm Delete", "Delete this Game?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success = self.run_query("EXEC sp_DeleteGame ?", (target_id,), fetch=False)

        elif action_type == "delete_tourn":
            confirm = QMessageBox.question(self, "Confirm", "Cancel this Tournament?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success = self.run_query("EXEC sp_CancelTournament ?", (target_id,), fetch=False)

        elif action_type == "delete_ref":
            confirm = QMessageBox.question(self, "Confirm", "Remove this Referee?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success = self.run_query("EXEC sp_DeleteReferee ?", (target_id,), fetch=False)

        elif action_type == "delete_player":
            confirm = QMessageBox.question(self, "Confirm", "Ban this Player?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success = self.run_query("EXEC sp_BanPlayer ?", (target_id,), fetch=False)

        elif action_type == "delete_pay":
            confirm = QMessageBox.question(self, "Confirm", "Reject Payment?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success = self.run_query("EXEC sp_RejectPayment ?", (target_id,), fetch=False)
        elif action_type == "view_proof":
            blob_data = extra.get("blob")
            if blob_data:
                self.show_image_dialog(blob_data)
            else:
                QMessageBox.warning(self, "Error", "No image data found.")
            return

        elif action_type == "show_msg":
            QMessageBox.information(self, "Info", extra)
            return

        elif action_type == "view_refs":
            self.show_referee_assignments_dialog(target_id)
            return

        elif action_type == "approve_ref":
            salary, ok = QInputDialog.getDouble(
                self, "Set Referee Salary",
                f"Enter monthly salary for Referee ID {target_id}:",
                500.00, 0, 100000, 2
            )
            if ok:
                success = self.run_query("EXEC sp_ApproveReferee ?, ?", (target_id, salary), fetch=False)
            else:
                return

        elif action_type == "approve_pay":
            success = self.run_query("EXEC sp_ApprovePayment ?", (target_id,), fetch=False)

        elif action_type == "edit_fee":
            current_fee = extra.get("current_fee", 0)
            new_fee, ok = QInputDialog.getInt(self, "Edit Fee", f"Enter new entry fee for Tournament ID {target_id}:",
                                              value=current_fee, min=0)
            if ok:
                success = self.run_query("UPDATE Tournament SET entry_fee = ? WHERE t_id = ?", (new_fee, target_id),
                                         fetch=False)

        elif action_type == "view_details":
            fmt = extra.get("format")
            count = extra.get("count")
            if fmt == "Knockout":
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_brackets)
                self.draw_bracket(target_id)
            else:
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_points_table)
                self.load_points_data(target_id)
            return

        if success:
            QMessageBox.information(self, "Success", "Action completed successfully.")
            self.refresh_page_data(self.ui.stackedWidget.currentWidget())

    # ----------------------------------------------------------------------
    # --- BRACKET VISUALIZER (TABLE VERSION) ---
    # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # --- BRACKET VISUALIZER (TABLE VERSION WITH WINNER COLUMN) ---
        # ----------------------------------------------------------------------
    def draw_bracket(self, tournament_id):
            # 1. Clear previous layout completely
            while self.ui.bracket_grid.count():
                item = self.ui.bracket_grid.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            # 2. Fetch Data
            query = """
                SELECT m.m_id, m.round_num, m.status, p.p_tag, m.winner_id, p.p_id
                FROM Match m
                LEFT JOIN Match_Participants mp ON m.m_id = mp.m_id
                LEFT JOIN Player p ON mp.p_id = p.p_id
                WHERE m.t_id = ?
                ORDER BY m.round_num, m.m_id
            """
            raw_data = self.run_query(query, (tournament_id,))

            if not raw_data:
                lbl_no_data = QLabel("No matches scheduled yet.")
                lbl_no_data.setStyleSheet("color: white; font-size: 16px;")
                lbl_no_data.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.bracket_grid.addWidget(lbl_no_data, 0, 0)
                return

            # 3. Process Data into Dict
            matches = {}
            for row in raw_data:
                m_id, r_num, status, p_name, winner_id, p_id = row

                if r_num not in matches: matches[r_num] = {}
                if m_id not in matches[r_num]:
                    matches[r_num][m_id] = {
                        'status': status,
                        'players': [],
                        'winner_id': winner_id
                    }
                if p_name:
                    matches[r_num][m_id]['players'].append((p_name, p_id))

            # 4. Draw Tables Round by Round
            grid_row_index = 0
            sorted_rounds = sorted(matches.keys())

            for r_num in sorted_rounds:
                round_data = matches[r_num]

                # -- Header Label --
                lbl_round = QLabel(f"ROUND {r_num}")
                lbl_round.setStyleSheet(
                    "color: #7b2cbf; font-weight: bold; font-size: 18px; margin-top: 10px; margin-bottom: 5px;")
                lbl_round.setAlignment(QtCore.Qt.AlignLeft)
                self.ui.bracket_grid.addWidget(lbl_round, grid_row_index, 0)
                grid_row_index += 1

                # -- Create Table for this Round --
                table = QtWidgets.QTableWidget()
                # UPDATED: 5 Columns now
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["Match ID", "Player 1", "Player 2", "Status", "Winner"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.verticalHeader().setVisible(False)
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table.setSelectionMode(QAbstractItemView.NoSelection)

                table.setStyleSheet("""
                    QTableWidget { background-color: #1e1e21; border: 1px solid #444; }
                    QHeaderView::section { background-color: #2a2a2d; color: white; padding: 4px; }
                    QTableWidget::item { color: #e0e0e0; padding: 5px; }
                """)

                # Fill Table
                table.setRowCount(len(round_data))
                row_idx = 0

                for m_id, m_info in round_data.items():
                    p1_text = "TBD"
                    p2_text = "TBD"
                    status_text = m_info['status']
                    participants = m_info['players']
                    winner_id = m_info['winner_id']
                    winner_name_text = "-"  # Default if no winner yet

                    if len(participants) >= 1: p1_text = participants[0][0]
                    if len(participants) >= 2: p2_text = participants[1][0]

                    # Create Items
                    item_p1 = QTableWidgetItem(p1_text)
                    item_p2 = QTableWidgetItem(p2_text)

                    # Logic to determine Winner Name and Highlight
                    if status_text == 'Completed' and winner_id:
                        # Find who won
                        for p_name, p_id in participants:
                            if p_id == winner_id:
                                winner_name_text = p_name
                                break

                        # Highlight the specific player cell in Green
                        if len(participants) >= 1 and participants[0][1] == winner_id:
                            item_p1.setForeground(QtGui.QColor("#4caf50"))
                            item_p1.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
                        elif len(participants) >= 2 and participants[1][1] == winner_id:
                            item_p2.setForeground(QtGui.QColor("#4caf50"))
                            item_p2.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

                    # Create Winner Item
                    item_winner = QTableWidgetItem(winner_name_text)
                    if winner_name_text != "-":
                        item_winner.setForeground(QtGui.QColor("#ffb74d"))  # Gold/Orange for winner column
                        item_winner.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

                    # Set Items
                    table.setItem(row_idx, 0, QTableWidgetItem(str(m_id)))
                    table.setItem(row_idx, 1, item_p1)
                    table.setItem(row_idx, 2, item_p2)
                    table.setItem(row_idx, 3, QTableWidgetItem(status_text))
                    table.setItem(row_idx, 4, item_winner)  # Add the winner column

                    row_idx += 1

                # Adjust Height
                row_height = 35
                header_height = table.horizontalHeader().height()
                total_height = (row_height * row_idx) + header_height + 10
                table.setMinimumHeight(total_height)
                table.setMaximumHeight(total_height)

                self.ui.bracket_grid.addWidget(table, grid_row_index, 0)
                grid_row_index += 1

            spacer = QWidget()
            spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.ui.bracket_grid.addWidget(spacer, grid_row_index, 0)

    # --- POINTS TABLE ---
    def load_points_data(self, tournament_id=None):
        query = """
            SELECT u.name, SUM(mp.total_points) as TotalPoints
            FROM Match_Participants mp
            JOIN Player p ON mp.p_id = p.p_id
            JOIN Users u ON p.p_id = u.u_id
            JOIN Match m ON mp.m_id = m.m_id
            WHERE m.t_id = ?
            GROUP BY u.name
            ORDER BY TotalPoints DESC
        """
        rows = self.run_query(query, (tournament_id,)) if tournament_id else []

        self.ui.table_points.setRowCount(0)
        if not rows: return

        self.ui.table_points.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.ui.table_points.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.ui.table_points.setItem(r, 1, QTableWidgetItem(str(row[1])))

    # --- LOADERS ---
    def load_view_tournaments(self):
        self.run_query("EXEC sp_AutoCancelExpiredTournaments", fetch=False)
        self.run_query("EXEC sp_StartReadyTournaments", fetch=False)

        query = "SELECT t_id, t_name, g_name, format, status, max_players FROM vw_AdminTournaments"
        rows = self.run_query(query)

        self.ui.table_view.setRowCount(0)
        if not rows: return

        self.ui.table_view.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:-1]):
                self.ui.table_view.setItem(r, c, QTableWidgetItem(str(val)))

            t_id = row[0]
            t_format = row[3]
            status = row[4]
            player_count = row[5]

            if status == 'Cancelled':
                btn_text = "Cancelled"
                btn_color = "#555555"
                action_data = ("show_msg", t_id, "This tournament was cancelled.")
            else:
                btn_text = "View Bracket" if t_format == "Knockout" else "View Points"
                btn_color = "#7b2cbf"
                action_data = ("view_details", t_id, {"format": t_format, "count": player_count})

            buttons_to_add = [
                {"text": btn_text, "color": btn_color, "action": action_data}
            ]

            if status == 'Ongoing':
                buttons_to_add.append({
                    "text": "Referees",
                    "color": "#e65100",
                    "action": ("view_refs", t_id, None)
                })

            self.add_action_buttons(self.ui.table_view, r, 5, buttons_to_add)

    def load_referees(self):
        rows_p = self.run_query("SELECT r_id, FullName, Specialization FROM vw_AdminRefereesPending")
        self.ui.table_ref_requests.setRowCount(0)
        if rows_p:
            self.ui.table_ref_requests.setRowCount(len(rows_p))
            for r, row in enumerate(rows_p):
                self.ui.table_ref_requests.setItem(r, 0, QTableWidgetItem(str(row[1])))
                self.ui.table_ref_requests.setItem(r, 1, QTableWidgetItem(str(row[2])))
                self.add_action_buttons(self.ui.table_ref_requests, r, 2, [
                    {"text": "Accept", "color": "#2e7d32", "action": ("approve_ref", row[0], None)},
                    {"text": "Reject", "color": "#d32f2f", "action": ("delete_ref", row[0], None)}
                ])

        rows_c = self.run_query("SELECT r_id, FullName FROM vw_AdminRefereesActive")
        self.ui.table_ref_current.setRowCount(0)
        if rows_c:
            self.ui.table_ref_current.setRowCount(len(rows_c))
            for r, row in enumerate(rows_c):
                self.ui.table_ref_current.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.ui.table_ref_current.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.add_action_buttons(self.ui.table_ref_current, r, 2, [
                    {"text": "Fire", "color": "#d32f2f", "action": ("delete_ref", row[0], None)}
                ])

    def load_payments(self):
        rows = self.run_query("SELECT pay_id, Username, TournamentName, amount, proof_image FROM vw_AdminPayments")
        self.ui.table_pay.setRowCount(0)
        if rows:
            self.ui.table_pay.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.ui.table_pay.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.ui.table_pay.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.ui.table_pay.setItem(r, 2, QTableWidgetItem(str(row[2])))
                self.ui.table_pay.setItem(r, 3, QTableWidgetItem(str(row[3])))

                proof_blob = row[4]
                buttons = [
                    {"text": "Approve", "color": "#2e7d32", "action": ("approve_pay", row[0], None)},
                    {"text": "Reject", "color": "#d32f2f", "action": ("delete_pay", row[0], None)}
                ]
                if proof_blob:
                    buttons.insert(0, {"text": "View Proof", "color": "#1976d2",
                                       "action": ("view_proof", row[0], {"blob": proof_blob})})
                self.add_action_buttons(self.ui.table_pay, r, 4, buttons)

    def load_players(self):
        rows = self.run_query("SELECT p_id, Gamertag, email FROM vw_AdminPlayers")
        self.ui.table_players.setRowCount(0)
        if rows:
            self.ui.table_players.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.ui.table_players.setItem(r, c, QTableWidgetItem(str(val)))
                self.add_action_buttons(self.ui.table_players, r, 3, [
                    {"text": "Ban", "color": "#d32f2f", "action": ("delete_player", row[0], None)}
                ])

    def load_cancel_tournaments(self):
        rows = self.run_query("SELECT t_id, t_name, start_date FROM vw_AdminTournaments WHERE status = 'Open'")
        self.ui.table_cancel.setRowCount(0)
        if rows:
            self.ui.table_cancel.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.ui.table_cancel.setItem(r, c, QTableWidgetItem(str(val)))
                self.add_action_buttons(self.ui.table_cancel, r, 3, [
                    {"text": "Cancel", "color": "#d32f2f", "action": ("delete_tourn", row[0], None)}
                ])

    def load_edit_tournaments(self):
        rows = self.run_query("SELECT t_id, t_name, entry_fee FROM vw_EditTournaments")
        self.ui.table_edit.setRowCount(0)
        if rows:
            self.ui.table_edit.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.ui.table_edit.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.ui.table_edit.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.ui.table_edit.setItem(r, 2, QTableWidgetItem(str(row[2])))
                self.add_action_buttons(self.ui.table_edit, r, 3, [
                    {"text": "Edit Fee", "color": "#1976d2", "action": ("edit_fee", row[0], {"current_fee": row[2]})}
                ])

    def load_system_history(self):
        rows = self.run_query("""
            SELECT u.name, h.entity, h.entity_id, h.action, h.timestamp
            FROM History h
            JOIN Users u ON h.user_id = u.u_id
            ORDER BY h.timestamp DESC
        """)
        self.ui.table_history.setRowCount(0)
        if not rows: return
        self.ui.table_history.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.ui.table_history.setItem(r, c, QTableWidgetItem(str(val)))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminDashboard("admin@esportify.com")
    window.showMaximized()
    sys.exit(app.exec_())