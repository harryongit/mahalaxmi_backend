import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logging import logger

def send_smtp_email(to_email: str, subject: str, body: str) -> bool:
    """
    Dynamically send email notifications using configured Gmail SMTP credentials.
    Gracefully handles authentication exceptions without breaking API calls.
    """
    host = settings.SMTP_HOST or "smtp.gmail.com"
    port = int(settings.SMTP_PORT or 587)
    username = settings.SMTP_USERNAME or settings.SMTP_USER or "pole2929@gmail.com"
    password = (settings.SMTP_PASSWORD or "").replace(" ", "").strip()
    from_email = settings.EMAILS_FROM_EMAIL or username
    from_name = settings.EMAILS_FROM_NAME or "Shri Mahalaxmi Mandir Kolhapur"

    if not username or not password:
        logger.warning("SMTP credentials missing. Dynamic email to %s skipped.", to_email)
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if "<html>" in body.lower() else "plain"))

        server = smtplib.SMTP(host, port, timeout=10)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()

        logger.info("Successfully sent SMTP email to %s via %s", to_email, host)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.warning(
            "Gmail SMTP 535 Auth Error: App Password for %s requires renewal at https://myaccount.google.com/apppasswords. Enquiry saved to MySQL.",
            username
        )
        return False
    except Exception as e:
        logger.error("Failed to send SMTP email to %s: %s", to_email, str(e))
        return False
