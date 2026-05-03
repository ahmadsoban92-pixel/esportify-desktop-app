Esportify – E-Sports Tournament Management System 🎮

Overview

Esportify is a comprehensive desktop application designed to streamline e-sports tournament management. Developed as a Database Systems semester project, it replaces messy Excel brackets with a centralized, automated, database-driven system.

The platform provides distinct, secure portals for Admins, Referees, and Players.

Features

First-Run Bootstrap Setup: A built-in setup wizard automatically detects if the system is fresh and securely creates the Master Admin account with email verification on the first launch.

Dynamic Brackets & Leaderboards: Bracket progression and live standings are calculated dynamically using optimized MS SQL Server Views and Stored Procedures, moving complex logic to the database layer.

Role-Based Architecture: Dedicated workflows and customized UI portals for Admins (management), Referees (scoring), and Players (participation).

Secure Authentication: Built-in email OTP verification for secure login, registration, and admin setup.

Data Security: Strict separation of credentials using .env environment variables to prevent hardcoded secrets.

Tournament Tracking: Support for different competitive formats including Knockout (Win/Loss) and Battle Royale (Placement/Points).

Tech Stack
Frontend: Python, PyQt5

Backend: MS SQL Server

Database Connectivity: pyodbc

Security & Configuration: python-dotenv, smtplib (Email verification)

Installation & Setup

1. Clone the repository

Bash

git clone https://github.com/ahmadsoban92-pixel/esportify-desktop-app.git

cd esportify-desktop-app

2. Install dependencies

Bash
pip install -r requirements.txt

3. Database Setup

Execute the provided dbproject.sql script in MS SQL Server Management Studio (SSMS) to build the schema, views, and stored procedures.

4. Environment Configuration

Create a file named .env in the root directory (use .env.example as a template) and add your database and email credentials:

Plaintext

DB_SERVER=YOUR_SERVER_NAME_HERE

DB_NAME=ESPORTS_SYSTEM

DB_USER=YOUR_USERNAME

DB_PASS=YOUR_PASSWORD

EMAIL_USER=your_email@gmail.com

EMAIL_PASS=your_app_password

5. Run the Application

Bash

python main_whole.py


Note: On your very first run, the system will automatically launch the First-Run Setup screen to securely register and verify the Master 

Admin account.


Authors

Soban Ahmad (Roll No. 114)

Huzaifa Rao (Roll No. 048)

Haris Malik (Roll No. 039)


Software Engineering