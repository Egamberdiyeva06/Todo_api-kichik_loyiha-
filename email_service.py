import asyncio
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "durdonaegamberdiyeva36@gmail.com"
EMAIL_PASSWORD = "ybqx ywfu oodb buli"

async def send_welcome_email(email: str):
    msg = EmailMessage()
    msg['Subject'] = "Welcome to our service!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content("Thank you for registering with our service.\
                    We are glad to have you on board!")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email muvaffaqiyatli yuborildi!")
    except Exception as e:
        print(f"Error sending email to {email}: {e}")

