from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Optional
from pydantic import EmailStr
import os
from datetime import datetime
import os
from fastapi_mail import FastMail, ConnectionConfig
from dotenv import load_dotenv



# Load .env variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
            MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
            USE_CREDENTIALS=True,
        )
        self.fastmail = FastMail(self.conf)
    
    async def send_welcome_email(self, user_email: str, user_name: str = None):
        """Send welcome email to new users"""
        subject = "Welcome to Black Germ Investment Platform!"
        body = f"""
        <html>
        <body>
            <h2>Welcome to Black Germ Investment Platform!</h2>
            <p>Dear {user_name or 'Investor'},</p>
            <p>Thank you for joining our secure cryptocurrency investment platform. Your account has been successfully created.</p>
            <p>Here's what you can do now:</p>
            <ul>
                <li>Complete your profile setup</li>
                <li>Add your wallet address</li>
                <li>Start your first investment</li>
                <li>Explore our AI-powered insights</li>
            </ul>
            <p>If you have any questions, our support team is here to help.</p>
            <p>Best regards,<br>Black Germ Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[user_email],
            body=body,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            print(f"✅ Welcome email sent successfully to {user_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending welcome email to {user_email}: {str(e)}")
            print(f"   Email config: {self.conf.MAIL_USERNAME} -> {self.conf.MAIL_FROM}")
            return False
    
    async def send_transaction_notification(self, user_email: str, transaction_type: str, amount: float, status: str):
        """Send transaction notification email"""
        subject = f"Transaction {status.title()} - Black Germ Platform"
        body = f"""
        <html>
        <body>
            <h2>Transaction {status.title()}</h2>
            <p>Your {transaction_type} transaction has been {status}.</p>
            <p><strong>Amount:</strong> ${amount:.2f}</p>
            <p><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p>You can view your transaction history in your dashboard.</p>
            <p>Best regards,<br>Black Germ Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[user_email],
            body=body,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            print(f"✅ Transaction notification sent successfully to {user_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending transaction email to {user_email}: {str(e)}")
            print(f"   Email config: {self.conf.MAIL_USERNAME} -> {self.conf.MAIL_FROM}")
            return False
    
    async def send_security_alert(self, user_email: str, alert_type: str, details: str):
        """Send security alert email"""
        subject = f"Security Alert - {alert_type}"
        body = f"""
        <html>
        <body>
            <h2>Security Alert</h2>
            <p>We detected {alert_type} on your account.</p>
            <p><strong>Details:</strong> {details}</p>
            <p>If this wasn't you, please contact our support team immediately.</p>
            <p>Best regards,<br>Black Germ Security Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[user_email],
            body=body,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            return True
        except Exception as e:
            print(f"Error sending security alert: {e}")
            return False
    
    async def send_investment_insights(self, user_email: str, insights: dict):
        """Send AI-powered investment insights"""
        subject = "Your Weekly Investment Insights"
        body = f"""
        <html>
        <body>
            <h2>Weekly Investment Insights</h2>
            <p>Here are your personalized investment insights:</p>
            <ul>
                <li><strong>Portfolio Value:</strong> ${insights.get('portfolio_value', 0):.2f}</li>
                <li><strong>Growth Rate:</strong> {insights.get('growth_rate', 0):.1f}%</li>
                <li><strong>Risk Level:</strong> {insights.get('risk_level', 'Moderate')}</li>
            </ul>
            <p><strong>Recommendations:</strong></p>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in insights.get('recommendations', [])])}
            </ul>
            <p>Best regards,<br>Black Germ AI Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[user_email],
            body=body,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            return True
        except Exception as e:
            print(f"Error sending insights email: {e}")
            return False

# Create a global instance
email_service = EmailService()