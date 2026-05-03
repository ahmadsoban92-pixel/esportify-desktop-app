import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QWidget, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from player_ui import Ui_PlayerWindow
from connection import get_db_connection
import style1


class PlayerDashboard(QtWidgets.QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user_email):
        super(PlayerDashboard, self).__init__()
        self.ui = Ui_PlayerWindow()
        self.ui.setupUi(self)

        self.current_user_email = user_email

        # 1. Fetch Player ID immediately
        self.current_player_id = self.get_player_id(user_email)

        print(f"DEBUG: Player Email: {self.current_user_email}, ID: {self.current_player_id}")

        if hasattr(style1, 'stylesheet') and style1.stylesheet:
            self.setStyleSheet(style1.stylesheet)

        # Navigation Setup
        self.nav_map = [
            (self.ui.btn_find_tournaments, self.ui.page_find),
            (self.ui.btn_my_tournaments, self.ui.page_my),
            (self.ui.btn_my_matches, self.ui.page_matches),
            (self.ui.btn_file_dispute, self.ui.page_dispute),
            (self.ui.btn_edit_profile, self.ui.page_profile),
        ]

        for btn, page in self.nav_map:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, p=page: self.refresh_page_data(p))

        self.ui.btn_logout.clicked.connect(self.perform_logout)
        self.ui.btn_back_standings.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_my))
        self.ui.btn_back_matches.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_my))

        # Logic Connections
        self.ui.btn_submit_dispute.clicked.connect(self.submit_dispute_form)
        self.ui.btn_save_profile.clicked.connect(self.update_profile)

        # Filters
        self.ui.combo_filter.currentIndexChanged.connect(self.load_my_tournaments)
        self.ui.input_search.textChanged.connect(self.load_available_tournaments)
        self.ui.combo_match_filter.currentIndexChanged.connect(self.load_my_match_history)

        # Initial Loads
        self.load_profile_data()
        self.refresh_page_data(self.ui.page_find)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_find)
        self.ui.btn_find_tournaments.setChecked(True)

    def perform_logout(self):
        self.logout_signal.emit()
        self.close()

    # --- DB HELPERS ---
    def get_player_id(self, email):
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT p_id FROM vw_PlayerLookup WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Error fetching Player ID: {e}")
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
        if page_widget == self.ui.page_find:
            self.load_available_tournaments()
        elif page_widget == self.ui.page_my:
            self.load_my_tournaments()
        elif page_widget == self.ui.page_matches:
            self.load_my_match_history()

    # --- 1. SUBMIT DISPUTE ---
    def submit_dispute_form(self):

        if not self.current_player_id:
            QMessageBox.critical(self, "Error", "Player ID not found.")
            return

        reported_player = self.ui.input_dispute_player.text().strip()
        reason = self.ui.input_dispute_reason.toPlainText().strip()

        if not reported_player or not reason:
            QMessageBox.warning(self, "Missing Details", "Please fill out the Player Gamertag and Reason.")
            return

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = "{CALL sp_SubmitDispute (?, ?, ?)}"
                cursor.execute(query, (self.current_player_id, reported_player, reason))

                row = cursor.fetchone()

                if row:
                    result_code = row[0]
                    message = row[1]

                    if result_code == 1:
                        conn.commit()
                        QMessageBox.information(self, "Success", message)
                        self.ui.input_dispute_player.clear()
                        self.ui.input_dispute_reason.clear()
                    else:
                        QMessageBox.warning(self, "Error", message)

                conn.close()
            except Exception as e:
                print(f"Error: {e}")
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    # --- 2. FIND TOURNAMENTS ---
    def load_available_tournaments(self):

        self.run_query("EXEC sp_AutoCancelExpiredTournaments", fetch=False)
        self.run_query("EXEC sp_StartReadyTournaments", fetch=False)
        search_text = self.ui.input_search.text().strip()
        query = "SELECT t_id, t_name, g_name, format, entry_fee FROM vw_OpenTournaments"

        rows = self.run_query(query)
        if not rows:
            self.ui.table_find.setRowCount(0)
            return

        filtered_rows = []
        for r in rows:
            if not search_text or search_text.lower() in r[1].lower() or search_text.lower() in r[2].lower():
                filtered_rows.append(r)

        self.ui.table_find.setRowCount(len(filtered_rows))
        for r_idx, row in enumerate(filtered_rows):
            for c, val in enumerate(row):
                self.ui.table_find.setItem(r_idx, c, QTableWidgetItem(str(val)))

            t_id = row[0]
            t_name = row[1]
            t_fee = row[4]

            self.add_action_button(self.ui.table_find, r_idx, 5, "Register", "#7b2cbf",
                                   lambda checked, tid=t_id, tn=t_name, f=t_fee,
                                          idx=r_idx: self.register_for_tournament(tid, tn, f, idx))



    # --- 3. MY TOURNAMENTS ---
        # REPLACE THIS FUNCTION IN player_main.py
    def load_my_tournaments(self):
            if not self.current_player_id: return

            # FIXED SQL: Used singular table names (Tournament, Registration)
            # FIXED COLUMNS: Used t.t_name instead of t.Name
            query = """
                SELECT t.t_id, t.t_name, g.g_name, r.status
                FROM Registration r
                JOIN Tournament t ON r.t_id = t.t_id
                JOIN Game g ON t.g_id = g.g_id
                WHERE r.p_id = ?
            """
            rows = self.run_query(query, (self.current_player_id,))

            category = self.ui.combo_filter.currentText()
            filtered = []

            if rows:
                for r in rows:
                    status = r[3]
                    # Logic remains the same
                    if category == "Participated" and status in ['Confirmed', 'approved', 'Completed']:
                        filtered.append(r)
                    elif category == "Upcoming" and status in ['pending', 'approved', 'Confirmed']:
                        filtered.append(r)
                    elif category == "All Tournaments":
                        filtered.append(r)

            self.populate_my_table(filtered)

            # ---------------------------------------------------------
            # FIX 1: POPULATE TABLE (Cleaned up, no nested functions)
            # ---------------------------------------------------------

    def populate_my_table(self, data):
        self.ui.table_my.setRowCount(len(data))
        for r, row in enumerate(data):
            self.ui.table_my.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.ui.table_my.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.ui.table_my.setItem(r, 2, QTableWidgetItem(str(row[2])))

            status_item = QTableWidgetItem(str(row[3]))
            if row[3] == 'Confirmed' or row[3] == 'approved':
                status_item.setForeground(QtGui.QColor("#4caf50"))  # Green
            elif row[3] == 'Pending' or row[3] == 'pending':
                status_item.setForeground(QtGui.QColor("#ff9800"))  # Orange
            elif row[3] == 'rejected':
                status_item.setForeground(QtGui.QColor("#d32f2f"))  # Red

            self.ui.table_my.setItem(r, 3, status_item)

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(5)

            btn_stand = QPushButton("Standings")
            btn_stand.setStyleSheet("background-color: #1976d2; color: white; padding: 5px; border-radius: 4px;")
            btn_stand.clicked.connect(lambda ch, name=row[1]: self.open_standings(name))

            btn_matches = QPushButton("My Matches")
            btn_matches.setStyleSheet("background-color: #7b2cbf; color: white; padding: 5px; border-radius: 4px;")
            btn_matches.clicked.connect(lambda ch, name=row[1]: self.open_my_matches(name))

            layout.addWidget(btn_stand)
            layout.addWidget(btn_matches)
            self.ui.table_my.setCellWidget(r, 5, container)

        # ---------------------------------------------------------
        # FIX 2: REGISTRATION LOGIC (Handle Rejection + Fix Schema)
        # ---------------------------------------------------------

    def register_for_tournament(self, t_id, t_name, fee, row_idx):
        if not self.current_player_id: return

        # 1. Check Existing Status (Fixing table name to 'Registration')
        check_query = "SELECT status FROM Registration WHERE p_id = ? AND t_id = ?"
        existing_rows = self.run_query(check_query, (self.current_player_id, t_id))

        if existing_rows:
            status = existing_rows[0][0]

            # If rejected, allow retry by deleting the old 'rejected' record first
            if status == 'rejected':
                confirm = QMessageBox.question(self, "Retry?", f"Your previous application was rejected. Try again?",
                                               QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    # Clean up old record so we can insert a new one
                    self.run_query("DELETE FROM Registration WHERE p_id = ? AND t_id = ?",
                                   (self.current_player_id, t_id), fetch=False)
                else:
                    return
            else:
                # If Pending, Approved, or Confirmed -> Block
                QMessageBox.warning(self, "Registered", f"You are already registered (Status: {status}).")
                return

        # 2. Parse Fee
        try:
            fee_val = float(str(fee).replace('$', '').replace('Free', '0').strip())
        except:
            fee_val = 0.0

        if fee_val > 0:
            msg = QMessageBox()
            msg.setWindowTitle("Payment")
            msg.setText(f"Please upload payment proof for {t_name} ({fee}).")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            if msg.exec_() == QMessageBox.Ok:
                path, _ = QFileDialog.getOpenFileName(self, "Upload Proof", "", "Images (*.png *.jpg *.jpeg)")
                if path:
                    # --- NEW LOGIC: CONVERT IMAGE TO BINARY ---
                    try:
                        with open(path, 'rb') as file:
                            binary_data = file.read()
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not read file: {e}")
                        return

                    # Send BINARY data to SQL, not the path string
                    pay_query = "{CALL sp_RegisterPaid (?, ?, ?, ?)}"

                    # Note: We pass 'binary_data' as the 4th argument
                    if self.run_query(pay_query, (self.current_player_id, t_id, fee_val, binary_data), fetch=False):
                        QMessageBox.information(self, "Success", "Payment proof uploaded. Awaiting Admin approval.")
                else:
                    return
        else:
            # Free Logic
            reg_query = "{CALL sp_RegisterFree (?, ?)}"
            if self.run_query(reg_query, (self.current_player_id, t_id), fetch=False):
                QMessageBox.information(self, "Success", f"Successfully registered for {t_name}!")

        # ---------------------------------------------------------
        # FIX 3: OPEN STANDINGS (Correct Indentation)
        # ---------------------------------------------------------

        # --- REPLACE THIS FUNCTION ---
    def open_standings(self, tournament_name):
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_standings)
            self.ui.lbl_standings_title.setText(f"Leaderboard: {tournament_name}")

            # This query handles both formats:
            # 1. Battle Royale: Sums Total Points
            # 2. Knockout: Counts the number of rounds won (to determine rank)
            query = """
                SELECT 
                    p.p_tag, 
                    CASE 
                        WHEN g.format = 'Battle Royale' THEN SUM(mp.total_points)
                        ELSE COUNT(CASE WHEN mp.is_winner = 1 THEN 1 END) -- Count wins for Knockout
                    END as Score
                FROM Match_Participants mp
                JOIN Match m ON mp.m_id = m.m_id
                JOIN Tournament t ON m.t_id = t.t_id
                JOIN Game g ON t.g_id = g.g_id
                JOIN Player p ON mp.p_id = p.p_id
                WHERE t.t_name = ?
                GROUP BY p.p_tag, g.format
                ORDER BY Score DESC
            """

            rows = self.run_query(query, (tournament_name,))

            self.ui.table_standings.setRowCount(0)
            if not rows: return

            self.ui.table_standings.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.ui.table_standings.setItem(r, 0, QTableWidgetItem(str(r + 1)))  # Rank
                self.ui.table_standings.setItem(r, 1, QTableWidgetItem(str(row[0])))  # Gamertag
                self.ui.table_standings.setItem(r, 2, QTableWidgetItem(str(row[1])))  # Score (Points or Wins)
    def open_my_matches(self, name):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_matches)
        self.ui.lbl_matches_title.setText(f"My Matches in: {name}")
        index = self.ui.combo_match_filter.findText(name)
        if index == -1:
            self.ui.combo_match_filter.addItem(name)
            self.ui.combo_match_filter.setCurrentText(name)
        else:
            self.ui.combo_match_filter.setCurrentIndex(index)

    # --- 4. MATCH HISTORY ---
        # --- REPLACE THIS FUNCTION ---
    def load_my_match_history(self):
            if not self.current_player_id: return

            # Updated Query to fetch Opponent
            query = """
                SELECT Name, Round, Opponent, Score, Result 
                FROM vw_PlayerMatches 
                WHERE PlayerID = ?
            """

            rows = self.run_query(query, (self.current_player_id,))

            selected_tourn = self.ui.combo_match_filter.currentText()
            filtered = []

            if rows:
                for r in rows:
                    t_name = r[0]
                    if selected_tourn == "All Matches" or selected_tourn == t_name:
                        filtered.append(r)

            # Set Column Count to 5 (Name, Round, Opponent, Score, Result)
            self.ui.table_matches.setColumnCount(5)
            self.ui.table_matches.setHorizontalHeaderLabels(["Tournament", "Round", "Opponent", "Score", "Result"])

            self.ui.table_matches.setRowCount(len(filtered))

            for r, row in enumerate(filtered):
                # row: Name(0), Round(1), Opponent(2), Score(3), Result(4)
                self.ui.table_matches.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.ui.table_matches.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.ui.table_matches.setItem(r, 2, QTableWidgetItem(str(row[2])))  # Opponent
                self.ui.table_matches.setItem(r, 3, QTableWidgetItem(str(row[3])))

                # Result Color Logic
                result_str = str(row[4])
                res_item = QTableWidgetItem(result_str)

                if "Win" in result_str or "Rank #1" == result_str:
                    res_item.setForeground(QtGui.QColor("#4caf50"))  # Green
                elif "Loss" in result_str:
                    res_item.setForeground(QtGui.QColor("#ff5555"))  # Red
                else:
                    res_item.setForeground(QtGui.QColor("#e0e0e0"))  # White/Grey

                self.ui.table_matches.setItem(r, 4, res_item)
    # --- 5. EDIT PROFILE LOGIC ---
    def load_profile_data(self):
        if not self.current_player_id: return
        query = """
            SELECT p.p_tag, u.email 
            FROM Player p 
            JOIN Users u ON p.p_id = u.u_id 
            WHERE p.p_id = ?
        """
        row = self.run_query(query, (self.current_player_id,), fetch=True)
        if row and row[0]:
            self.ui.input_prof_gamertag.setText(str(row[0][0]))
            self.ui.input_prof_email.setText(str(row[0][1]))

    def update_profile(self):
        new_tag = self.ui.input_prof_gamertag.text().strip()
        curr_pass = self.ui.input_prof_pass.text().strip()
        new_pass = self.ui.input_prof_new_pass.text().strip()

        if not new_tag or not curr_pass:
            QMessageBox.warning(self, "Error", "Gamertag and Current Password are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Users WHERE u_id = ?", (self.current_player_id,))
            row = cursor.fetchone()
            if not row or row[0] != curr_pass:
                QMessageBox.warning(self, "Error", "Incorrect current password.")
                return

            cursor.execute("UPDATE Player SET p_tag = ? WHERE p_id = ?", (new_tag, self.current_player_id))
            if new_pass:
                cursor.execute("UPDATE Users SET password = ? WHERE u_id = ?", (new_pass, self.current_player_id))

            conn.commit()
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.ui.input_prof_pass.clear()
            self.ui.input_prof_new_pass.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Update failed: {e}")
        finally:
            conn.close()

    def add_action_button(self, table, row, col, text, color, func):
        btn = QPushButton(text)
        btn.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 4px; padding: 6px; font-weight: bold;")
        btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn.clicked.connect(func)
        table.setCellWidget(row, col, btn)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PlayerDashboard("hmalik7@gmail.com")
    window.showMaximized()
    sys.exit(app.exec_())