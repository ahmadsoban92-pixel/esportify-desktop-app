# style1.py

stylesheet = """
/* =======================================================
   1. GLOBAL RESET
   ======================================================= */
QMainWindow, QWidget {
    background-color: #0f0b12; 
    color: #e0e0e0;            
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}

/* =======================================================
   2. SIDEBAR
   ======================================================= */
QFrame#frame {
    background-color: #09050b; 
    border-right: 1px solid #2e003e;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
QFrame#frame QPushButton {
    background-color: transparent;
    border: none;
    text-align: left;
    padding-left: 20px;
    color: #a0a0a0;
    font-size: 14px;
    height: 45px;
    border-radius: 8px;
    margin: 2px 10px;
}
QFrame#frame QPushButton:hover {
    background-color: #1f1429;
    color: white;
    border-left: 3px solid #bd93f9;
}
QFrame#frame QPushButton:checked {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7b2cbf, stop:1 #5a189a);
    color: white;
    font-weight: bold;
    border-left: 3px solid #ffffff; 
}
QLabel#label {
    font-size: 24px;
    font-weight: bold;
    color: white;
    
    /* THE PURPLE BORDER & GLOW */
    border: 2px solid #bd93f9; 
    border-radius: 10px;
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4a148c, stop:1 #7b2cbf);
    
    /* SPACING */
    padding: 10px;
    margin: 15px; /* Adds space around the box so it doesn't touch edges */
    qproperty-alignment: AlignCenter;
}

/* =======================================================
   3. THE CONTENT CARDS
   ======================================================= */
QFrame#frame_2, QFrame#frame_edit, QFrame#frame_cancel, QFrame#frame_ref, QFrame#frame_pay, QFrame#frame_rep {
    background-color: #151518;
    border: 1px solid #4a148c;
    border-radius: 15px;
}
/* Generic Labels inside Cards */
QFrame QLabel {
    color: #d1d1d1;
    font-weight: 500;
    background-color: transparent;
    border: none;
}

/* =======================================================
   4. THE TITLE HEADERS
   ======================================================= */
QLabel#create_tournament_label, 
QLabel#view_tournnament_label, 
QLabel#header_edit, 
QLabel#header_cancel, 
QLabel#header_referee, 
QLabel#header_payment, 
QLabel#header_report,
QLabel#header_details {
    font-size: 24px;
    font-weight: bold;
    color: white;
    border: 2px solid #bd93f9; 
    border-radius: 10px;
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4a148c, stop:1 #7b2cbf);
    padding: 15px;
    margin-bottom: 25px;
    qproperty-alignment: AlignCenter;
}

/* =======================================================
   5. INPUTS & TABLES
   ======================================================= */
QLineEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {
    background-color: #1a1a1d; 
    border: 1px solid #333;
    border-radius: 6px;
    padding: 6px 10px;
    color: white;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #d500f9; 
    background-color: #202023;
}
QTableWidget {
    background-color: #161619;
    alternate-background-color: #1e1e21;
    gridline-color: #2a2a2d;
    border: 1px solid #333;
    border-radius: 8px;
}
QHeaderView::section {
    background-color: #0f0b12;
    color: #bd93f9;
    border: none;
    border-bottom: 2px solid #7b2cbf;
    padding: 8px;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #4a148c;
    color: white;
}

/* --- BUTTONS INSIDE TABLES (Specific Fix) --- */
QTableWidget QPushButton {
    background-color: #333;
    border: 1px solid #555;
    border-radius: 4px;
    color: white;
    font-weight: bold;
    padding: 5px;
    margin: 2px;
    min-width: 60px;
}
QTableWidget QPushButton:hover {
    background-color: #555;
    border: 1px solid #7b2cbf; /* Purple border on hover */
}
QTableWidget QPushButton:pressed {
    background-color: #222;
}

/* General Buttons */
QPushButton#submit_create_tour_button, QPushButton#btn_open, QPushButton#btn_cancel_action, QPushButton#btn_add_game, QPushButton#btn_search_p {
    background-color: #7b2cbf;
    color: white;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
    padding: 8px;
}
QPushButton:hover {
    background-color: #9d4edd;
}

QScrollArea {
    background: transparent;
    border: none;
}
"""