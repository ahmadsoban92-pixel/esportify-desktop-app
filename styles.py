# styles.py

QSS_STYLES = {
    # --- ESPORTIFY Logo (Fixed Padding) ---
    "logo_label": """
        QLabel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white;
            font-size: 28px; /* Slightly smaller to fit */
            font-weight: bold;
            padding: 15px;
            border-radius: 10px;
            min-height: 40px;
            qproperty-alignment: AlignCenter;
        }
    """,

    # --- Headings & Titles ---
    "title_label": "color: white; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 10px;",
    "subtitle_label": "color: #9CA3AF; font-size: 13px; margin-bottom: 20px;",
    "standard_label": "color: #D1D5DB; font-size: 14px; margin-top: 5px; font-weight: 500;",

    # --- Input Fields (Better Spacing) ---
    "input_field": """
        QLineEdit {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 6px;
            padding: 8px 12px;
            color: white;
            font-size: 14px;
            min-height: 25px; /* Ensures text isn't squashed */
        }
        QLineEdit:focus {
            border: 2px solid #3B82F6; 
            background-color: #374151;
        }
    """,

    # --- Radio Buttons ---
    "radio_button": """
        QRadioButton { 
            color: #E5E7EB; 
            font-size: 14px; 
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
    """,

    # --- Main Login Button (Fixed Clipping) ---
    "login_button": """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8); 
            color: white;
            font-size: 15px;
            font-weight: bold;
            padding: 12px;
            border: none;
            border-radius: 6px;
            min-height: 25px; /* Critical Fix */
            margin-top: 15px;
        }
        QPushButton:hover { background: #3B82F6; }
        QPushButton:pressed { background: #1E40AF; }
    """,

    # --- Secondary Buttons (Gray) ---
    "create_account_button": """
        QPushButton {
            background-color: #374151;
            color: white;
            font-size: 13px;
            font-weight: 600;
            padding: 10px;
            border: 1px solid #4B5563;
            border-radius: 6px;
            min-height: 25px; /* Critical Fix */
            margin-top: 5px;
        }
        QPushButton:hover { background-color: #4B5563; }
        QPushButton:pressed { background-color: #1F2937; }
    """,

    # --- Link Button ---
    "link_button": """
        QPushButton {
            background: transparent;
            border: none;
            color: #A78BFA; 
            font-size: 13px;
            text-align: right;
            margin-bottom: 5px;
        }
        QPushButton:hover { text-decoration: underline; color: #C4B5FD; }
    """,

    "window_background": "background-color: #0f0b12; color: white; font-family: 'Segoe UI', sans-serif;"
}