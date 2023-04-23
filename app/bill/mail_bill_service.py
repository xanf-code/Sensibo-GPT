import smtplib
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

sender=os.environ.get("SENDER_EMAIL")
receiver=os.environ.get("RECEIVER_EMAIL")
password=os.environ.get("SENDER_PASSWORD")

def email_bill(hours, cost):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = sender
    sender_password = password
    recipient_email = receiver

    message = MIMEMultipart("alternative")
    message["Subject"] = "AC Usage Bill Update."
    message["From"] = sender_email
    message["To"] = recipient_email

    text = f"Electricity bill for {hours} hours of AC usage is approximately: Rs {cost}"
    html = f"""\
    <html>
        <body>
            <p>Electricity bill for <b>{hours}</b> hours of AC usage is approximately: <b>₹{cost}</b></p>
        </body>
    </html>
    """

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())