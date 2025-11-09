import smtplib
from email.message import EmailMessage

def send_alert():
    sender = "your_email@gmail.com"
    app_password = "your_app_password"
    receiver = "receiver_email@gmail.com"

    msg = EmailMessage()
    msg["Subject"] = "⚠️ Suspicious Activity Detected!"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("Suspicious activity detected in CCTV footage.")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        print("📧 Email alert sent successfully.")
    except Exception as e:
        print("❌ Email sending failed:", e)
