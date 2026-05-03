import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QWidget, QHBoxLayout, QMessageBox
import style1
from PyQt5.QtCore import pyqtSignal
from referee_ui import Ui_RefereeWindow
from connection import get_db_connection


class RefereeDashboard(QtWidgets.QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user_email):
        super(RefereeDashboard, self).__init__()
        self.ui = Ui_RefereeWindow()
        self.ui.setupUi(self)

        if hasattr(style1, 'stylesheet'):
            self.setStyleSheet(style1.stylesheet)

        # --- DYNAMIC INITIALIZATION ---
        self.current_referee_email = user_email
        self.current_referee_id = self.get_referee_id(user_email)
        self.current_match_type = None  # Track if we are in BR or KO mode

        print(f"DEBUG: Referee Email: {self.current_referee_email}, ID: {self.current_referee_id}")

        # Navigation
        self.nav_map = [
            (self.ui.btn_assigned, self.ui.page_assigned),
            (self.ui.btn_history, self.ui.page_history),
            (self.ui.btn_disputes, self.ui.page_disputes),
            (self.ui.btn_profile, self.ui.page_profile),
        ]

        for btn, page in self.nav_map:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, p=page: self.refresh_page_data(p))

        self.ui.btn_logout.clicked.connect(self.perform_logout)

        # Match Logic Buttons
        # Connect BOTH submit buttons to the same handler
        self.ui.btn_submit_pts.clicked.connect(self.submit_match_result)
        self.ui.btn_submit_ko.clicked.connect(self.submit_match_result)

        self.ui.btn_back_pts.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_assigned))
        self.ui.btn_back_ko.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_assigned))

        # Profile Logic Connection
        self.ui.btn_save_profile.clicked.connect(self.update_profile)

        # Initial Load
        self.refresh_page_data(self.ui.page_assigned)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_assigned)
        self.ui.btn_assigned.setChecked(True)

    def perform_logout(self):
        self.logout_signal.emit()
        self.close()

    # --- DB HELPERS ---
    def get_referee_id(self, email):
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT r_id FROM vw_RefereeLookup WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Error fetching Referee ID: {e}")
            return None

    def run_query(self, query, params=(), fetch=True):
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                data = cursor.fetchall()
                conn.close()
                return data
            else:
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    def refresh_page_data(self, page_widget):
        self.ui.stackedWidget.setCurrentWidget(page_widget)
        if page_widget == self.ui.page_assigned:
            self.load_assigned_matches()
        elif page_widget == self.ui.page_history:
            self.load_history()
        elif page_widget == self.ui.page_disputes:
            self.load_disputes()
        elif page_widget == self.ui.page_profile:
            self.load_profile()

    def add_action_button(self, table, row, col, text, color, func):
        btn = QPushButton(text)
        btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 6px;")
        btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn.clicked.connect(func)
        table.setCellWidget(row, col, btn)

    # ---------------------------------------------------------
    # --- 1. PROFILE LOGIC ---
    # ---------------------------------------------------------
    def load_profile(self):
        if not self.current_referee_id: return
        query = "SELECT name, email FROM Users WHERE u_id = ?"
        rows = self.run_query(query, (self.current_referee_id,))
        if rows:
            name = rows[0][0]
            email = rows[0][1]
            self.ui.input_prof_name.setText(str(name))
            self.ui.input_prof_email.setText(str(email))
            self.ui.input_prof_email.setReadOnly(True)
            self.ui.input_prof_email.setStyleSheet("background-color: #333; color: #888; border: 1px solid #555;")

    def update_profile(self):
        new_name = self.ui.input_prof_name.text().strip()
        curr_pass = self.ui.input_prof_pass.text().strip()
        new_pass = self.ui.input_prof_new_pass.text().strip()

        if not new_name or not curr_pass:
            QMessageBox.warning(self, "Missing Data", "Name and Current Password are required.")
            return

        conn = get_db_connection()
        if not conn: return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Users WHERE u_id = ?", (self.current_referee_id,))
            row = cursor.fetchone()

            if not row or row[0] != curr_pass:
                QMessageBox.warning(self, "Auth Failed", "Incorrect current password.")
                return

            cursor.execute("UPDATE Users SET name = ? WHERE u_id = ?", (new_name, self.current_referee_id))
            if new_pass:
                cursor.execute("UPDATE Users SET password = ? WHERE u_id = ?", (new_pass, self.current_referee_id))

            conn.commit()
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.ui.input_prof_pass.clear()
            self.ui.input_prof_new_pass.clear()
        except Exception as e:
            if conn: conn.rollback()
            QMessageBox.critical(self, "Error", f"Update failed: {e}")
        finally:
            conn.close()

    # ---------------------------------------------------------
    # --- 2. ASSIGNED MATCHES ---
    # ---------------------------------------------------------
    def load_assigned_matches(self):
        if not self.current_referee_id: return

        query = """
                SELECT m_id, t_name, g_name, format, status
                FROM vw_RefereeMatches
                WHERE r_id = ? AND status <> 'Completed'
                """
        rows = self.run_query(query, (self.current_referee_id,))
        if rows is None: return

        self.ui.table_assigned.setColumnCount(6)
        self.ui.table_assigned.setHorizontalHeaderLabels(["ID", "Tournament", "Game", "Format", "Status", "Action"])
        self.ui.table_assigned.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.ui.table_assigned.setRowCount(0)
        self.ui.table_assigned.setRowCount(len(rows))

        for r, row in enumerate(rows):
            self.ui.table_assigned.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.ui.table_assigned.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.ui.table_assigned.setItem(r, 2, QTableWidgetItem(str(row[2])))
            self.ui.table_assigned.setItem(r, 3, QTableWidgetItem(str(row[3])))
            self.ui.table_assigned.setItem(r, 4, QTableWidgetItem(str(row[4])))

            match_id = row[0]
            game_format = row[3]

            self.add_action_button(
                self.ui.table_assigned, r, 5, "Manage Match", "#7b2cbf",
                lambda checked, t=game_format, i=match_id: self.open_scoring_room(t, i)
            )

    def open_scoring_room(self, match_type, match_id):
        print(f"DEBUG: Opening room for Match #{match_id} ({match_type})")
        self.current_match_id = match_id

        # --- 1. FETCH PLAYERS ---
        query = "SELECT Gamertag FROM vw_MatchPlayers WHERE m_id = ?"
        rows = self.run_query(query, (match_id,))
        players = [r[0] for r in rows] if rows else []

        if not players:
            QMessageBox.warning(self, "Match Empty", "No players found for this match.")
            return

        # --- 2. DETERMINE MODE ---
        # Check if "Battle" is in the type string (handles "Battle Royale" vs "BattleRoyale")
        if "Battle" in match_type:
            self.current_match_type = "BR"
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_score_points)
            self.ui.lbl_match_info_pts.setText(f"SCORING: Match #{match_id} (Battle Royale)")
            self.load_points_input(players)
        else:
            self.current_match_type = "KO"
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_score_ko)

            p1 = players[0] if len(players) > 0 else "TBD"
            p2 = players[1] if len(players) > 1 else "TBD"

            self.ui.lbl_player_a.setText(p1)
            self.ui.lbl_player_b.setText(p2)

            self.ui.input_score_a.setValue(0)
            self.ui.input_score_b.setValue(0)

            self.ui.combo_winner.clear()
            # Add valid options
            self.ui.combo_winner.addItems(["Select Winner...", p1, p2])

    def load_points_input(self, players):
        try:
            self.ui.table_points.cellChanged.disconnect()
        except TypeError:
            pass

        self.ui.table_points.setRowCount(len(players))

        for r, player in enumerate(players):
            # Name (Read Only)
            item = QTableWidgetItem(player)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.table_points.setItem(r, 0, item)

            # Kills (Editable)
            self.ui.table_points.setItem(r, 1, QTableWidgetItem("0"))

            # Placement (Editable)
            self.ui.table_points.setItem(r, 2, QTableWidgetItem("0"))

            # Total (Read Only)
            item_total = QTableWidgetItem("0")
            item_total.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.table_points.setItem(r, 3, item_total)

        self.ui.table_points.cellChanged.connect(self.auto_calculate_score)

    RANK_POINTS = {1: 15, 2: 12, 3: 10, 4: 8, 5: 6, 6: 4, 7: 2, 8: 1}

    def auto_calculate_score(self, row, column):
        if column not in [1, 2]: return

        item_kills = self.ui.table_points.item(row, 1)
        item_rank = self.ui.table_points.item(row, 2)

        txt_kills = item_kills.text() if item_kills else "0"
        txt_rank = item_rank.text() if item_rank else "0"

        if not txt_kills.isdigit() or not txt_rank.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter numbers only.")
            self.reset_cell(row, column)
            return

        kills = int(txt_kills)
        rank = int(txt_rank)

        total_players = self.ui.table_points.rowCount()

        if column == 2 and rank > total_players:
            QMessageBox.warning(self, "Invalid Rank", f"Rank cannot be higher than {total_players}.")
            self.reset_cell(row, column)
            return

        placement_pts = 0
        if rank > 0:
            placement_pts = self.RANK_POINTS.get(rank, 0)

        total_score = kills + placement_pts

        self.ui.table_points.blockSignals(True)
        self.ui.table_points.item(row, 3).setText(str(total_score))
        self.ui.table_points.blockSignals(False)

    def reset_cell(self, row, col):
        self.ui.table_points.blockSignals(True)
        self.ui.table_points.item(row, col).setText("0")
        self.ui.table_points.blockSignals(False)

    # ---------------------------------------------------------
    # --- 3. SUBMIT LOGIC (HANDLES BOTH BR AND KO) ---
    # ---------------------------------------------------------
        # ---------------------------------------------------------
        # --- 3. SUBMIT LOGIC (FIXED CRASH & ADDED VALIDATION) ---
        # ---------------------------------------------------------
    def submit_match_result(self):
            if not hasattr(self, 'current_match_id'): return

            confirm = QMessageBox.question(
                self, "Finalize Match",
                "Are you sure you want to submit results?\nThis will mark the match as COMPLETED.",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.No: return

            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()

            try:
                # --- LOGIC A: BATTLE ROYALE (POINTS TABLE) ---
                if self.current_match_type == "BR":
                    rows = self.ui.table_points.rowCount()

                    if rows == 0:
                        QMessageBox.warning(self, "Error", "Table is empty.")
                        return  # Finally block will close conn

                    for r in range(rows):
                        gamertag = self.ui.table_points.item(r, 0).text()
                        kills = int(self.ui.table_points.item(r, 1).text())
                        rank = int(self.ui.table_points.item(r, 2).text())
                        total = int(self.ui.table_points.item(r, 3).text())

                        cursor.execute(
                            "{CALL sp_UpdatePlayerStats (?, ?, ?, ?, ?)}",
                            (self.current_match_id, gamertag, kills, rank, total)
                        )

                # --- LOGIC B: KNOCKOUT (1v1 INPUTS) ---
                elif self.current_match_type == "KO":
                    p1_tag = self.ui.lbl_player_a.text()
                    p2_tag = self.ui.lbl_player_b.text()

                    score_a = self.ui.input_score_a.value()
                    score_b = self.ui.input_score_b.value()

                    winner_selection = self.ui.combo_winner.currentText()

                    # 1. CHECK: Did they select a winner?
                    if winner_selection == "Select Winner...":
                        QMessageBox.warning(self, "Incomplete", "Please select a Winner from the dropdown.")
                        return  # Returns safely, 'finally' block closes connection

                    # 2. CHECK: Does the winner actually have the higher score?
                    if winner_selection == p1_tag and score_a < score_b:
                        QMessageBox.warning(self, "Logic Error",
                                            f"You selected {p1_tag} as winner, but they have fewer points ({score_a}) than {p2_tag} ({score_b}).")
                        return

                    if winner_selection == p2_tag and score_b < score_a:
                        QMessageBox.warning(self, "Logic Error",
                                            f"You selected {p2_tag} as winner, but they have fewer points ({score_b}) than {p1_tag} ({score_a}).")
                        return

                    # Determine Ranks (1st = Winner, 2nd = Loser)
                    p1_rank = 1 if winner_selection == p1_tag else 2
                    p2_rank = 1 if winner_selection == p2_tag else 2

                    # Update Player A
                    cursor.execute(
                        "{CALL sp_UpdatePlayerStats (?, ?, ?, ?, ?)}",
                        (self.current_match_id, p1_tag, 0, p1_rank, score_a)
                    )

                    # Update Player B
                    cursor.execute(
                        "{CALL sp_UpdatePlayerStats (?, ?, ?, ?, ?)}",
                        (self.current_match_id, p2_tag, 0, p2_rank, score_b)
                    )

                # --- FINALIZE ---
                cursor.execute("{CALL sp_FinalizeMatch (?)}", (self.current_match_id,))
                conn.commit()

                QMessageBox.information(self, "Success", "Match results saved successfully!")

                # Reset UI
                self.refresh_page_data(self.ui.page_history)
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_history)
                self.load_assigned_matches()

            except Exception as e:
                if conn: conn.rollback()
                print(f"Error saving match: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save results: {e}")
            finally:
                # This ensures connection closes exactly once, preventing the crash
                conn.close()
    # ---------------------------------------------------------
    # --- 4. HISTORY & DISPUTES (UNCHANGED) ---
    # ---------------------------------------------------------
    def load_history(self):
        if not self.current_referee_id: return
        query = "SELECT m_id, t_name, g_name, WinnerName, DatePlayed FROM vw_RefereeHistory WHERE r_id = ?"
        rows = self.run_query(query, (self.current_referee_id,))
        if rows is None:
            self.ui.table_history.setRowCount(0)
            return
        self.ui.table_history.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.ui.table_history.setItem(r, c, item)

    def load_disputes(self):
        if not self.current_referee_id: return
        query = "SELECT dispute_id, ReportedName, reason FROM vw_RefereeDisputes WHERE referee_id IS NULL AND status = 'pending'"
        rows = self.run_query(query)
        if rows is None:
            self.ui.table_disputes.setRowCount(0)
            return
        self.ui.table_disputes.setRowCount(len(rows))
        for r, row in enumerate(rows):
            dispute_id = row[0]
            self.ui.table_disputes.setItem(r, 0, QTableWidgetItem(str(dispute_id)))
            self.ui.table_disputes.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.ui.table_disputes.setItem(r, 2, QTableWidgetItem(str(row[2])))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setSpacing(10)

            btn_approve = QPushButton("Approve")
            btn_approve.setStyleSheet("background-color: #2e7d32; color: white; border-radius: 4px; padding: 4px;")
            btn_approve.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn_approve.clicked.connect(lambda checked, d=dispute_id: self.handle_dispute_action(d, "Approved"))

            btn_reject = QPushButton("Reject")
            btn_reject.setStyleSheet("background-color: #d32f2f; color: white; border-radius: 4px; padding: 4px;")
            btn_reject.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn_reject.clicked.connect(lambda checked, d=dispute_id: self.handle_dispute_action(d, "Rejected"))

            layout.addWidget(btn_approve)
            layout.addWidget(btn_reject)
            self.ui.table_disputes.setCellWidget(r, 3, container)

    def handle_dispute_action(self, dispute_id, action):
        confirm = QMessageBox.question(self, "Confirm", f"Mark dispute as {action}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No: return
        query = "{CALL sp_ResolveDispute (?, ?, ?)}"
        success = self.run_query(query, (dispute_id, action, self.current_referee_id), fetch=False)
        if success:
            self.load_disputes()
        else:
            QMessageBox.critical(self, "Error", "Failed to update status.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RefereeDashboard("sobanahmad92@gmail.com")
    window.showMaximized()
    sys.exit(app.exec_())