import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Force reload of environment variables
load_dotenv(override=True)

def test_smtp_connection():
    # Print environment variables (without password)
    print("Environment settings:")
    print(f"SMTP Server: {os.getenv('SMTP_SERVER')}")
    print(f"SMTP Port: {os.getenv('SMTP_PORT')}")
    print(f"SMTP Username: {os.getenv('SMTP_USERNAME')}")
    print(f"From Email: {os.getenv('FROM_EMAIL')}")

    try:
        # Get credentials from .env
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL')

        if not all([smtp_server, smtp_port, smtp_username, smtp_password, from_email]):
            print("Error: Missing required environment variables")
            return

        print(f"\nAttempting to connect to {smtp_server}:{smtp_port}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = from_email  # Sending to ourselves as a test
        msg['Subject'] = 'SMTP Test Email'
        body = 'This is a test email to verify SMTP functionality.'
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server with debugging
        print("Establishing connection...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Enable debug output
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(smtp_username, smtp_password)
        
        print("Sending email...")
        server.send_message(msg)
        
        print("Email sent successfully!")
        server.quit()

    except Exception as e:
        print(f"\nError occurred:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        if hasattr(e, 'smtp_code'):
            print(f"SMTP Code: {e.smtp_code}")
        if hasattr(e, 'smtp_error'):
            print(f"SMTP Error: {e.smtp_error}")

if __name__ == "__main__":
    test_smtp_connection()
