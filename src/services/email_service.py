"""Email and notification services."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Handle email operations."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def save_config(self, smtp_server: str, smtp_port: int, sender_email: str,
                   sender_password: str, recipient_email: str) -> bool:
        """Save email configuration."""
        if not all([smtp_server, sender_email, sender_password, recipient_email]):
            raise ValueError("All email config fields are required")
        return self.db.save_email_config(smtp_server, smtp_port, sender_email, sender_password, recipient_email)
    
    def get_config(self) -> dict:
        """Get email configuration."""
        return self.db.get_email_config()
    
    def send_email(self, subject: str, body: str, recipient: str = None) -> bool:
        """Send an email."""
        config = self.get_config()
        if not config:
            raise RuntimeError("Email configuration is missing")
        
        server = config['smtp_server']
        port = config['smtp_port']
        sender = config['sender_email']
        password = config['sender_password']
        to_addr = recipient or config['recipient_email']
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = to_addr
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(server, int(port)) as smtp:
                smtp.starttls()
                smtp.login(sender, password)
                smtp.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_low_stock_alerts(self, low_stock_items: list) -> bool:
        """Send low stock alert email."""
        if not low_stock_items:
            return False
        
        body = "Low stock alert:\n\n"
        for item in low_stock_items:
            name = item[0] if isinstance(item, tuple) else item.get('item_name', 'Unknown')
            qty = item[1] if isinstance(item, tuple) else item.get('quantity', 0)
            threshold = item[2] if isinstance(item, tuple) else item.get('threshold', 0)
            body += f"- {name}: Qty={qty}, Threshold={threshold}\n"
        
        try:
            return self.send_email("BizHub - Low Stock Alerts", body)
        except Exception as e:
            print(f"Error sending low stock alerts: {e}")
            return False
