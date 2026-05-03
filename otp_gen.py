import os
import random
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

# --- CONFIGURATION ---
# 2. Fetch the credentials securely from the environment
FROM_EMAIL = os.getenv('EMAIL_USER')
APP_PASSWORD = os.getenv('EMAIL_PASS')


def send_otp_email(to_email, subject="ESPORTIFY Verification"):
    """
    Generates a 6-digit OTP, sends it to the specified email,
    and returns the OTP string.
    Returns None if sending failed.
    """
    
    # Failsafe: Check if credentials loaded properly
    if not FROM_EMAIL or not APP_PASSWORD:
        print("ERROR: Email credentials not found in .env file.")
        return None

    # 1. Generate OTP
    otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])

    # 2. Prepare Email
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg.set_content(
        f"Hello,\n\nYour Verification Code is: {otp_code}\n\n"
        f"Please do not share this code with anyone.\n\n"
        f"- The Esportify Team"
    )

    # 3. Send Email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"DEBUG: Email sent successfully to {to_email}")
        return otp_code  # Success! Return the code to the app

    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        return None  # Failure