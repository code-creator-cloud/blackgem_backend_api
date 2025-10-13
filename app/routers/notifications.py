from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from app.database import get_db
from app import models, schemas, auth
from app.email_service import email_service

router = APIRouter()

@router.post("/send-welcome")
async def send_welcome_email(
    user_email: str,
    user_name: str = None,
    background_tasks: BackgroundTasks = None
):
    """Send welcome email to new user"""
    success = await email_service.send_welcome_email(user_email, user_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send welcome email")
    return {"message": "Welcome email sent successfully"}

@router.post("/send-transaction-notification")
async def send_transaction_notification(
    user_email: str,
    transaction_type: str,
    amount: float,
    status: str,
    background_tasks: BackgroundTasks = None
):
    """Send transaction notification email"""
    success = await email_service.send_transaction_notification(user_email, transaction_type, amount, status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send transaction notification")
    return {"message": "Transaction notification sent successfully"}

@router.post("/send-security-alert")
async def send_security_alert(
    alert: schemas.UserSecurityAlert,
    background_tasks: BackgroundTasks = None
):
    """Send security alert email"""
    success = await email_service.send_security_alert(alert.user_email, alert.alert_type, alert.details)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send security alert")
    return {"message": "Security alert sent successfully"}

@router.post("/send-investment-insights")
async def send_investment_insights(
    user_email: str,
    insights: Dict,
    background_tasks: BackgroundTasks = None
):
    """Send AI-powered investment insights email"""
    success = await email_service.send_investment_insights(user_email, insights)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send investment insights")
    return {"message": "Investment insights sent successfully"}

@router.get("/notification-preferences")
async def get_notification_preferences(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get user's notification preferences"""
    return {
        "email_notifications": True,
        "transaction_alerts": True,
        "security_alerts": True,
        "investment_insights": True,
        "marketing_emails": False
    }

@router.put("/notification-preferences")
async def update_notification_preferences(
    preferences: Dict,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update user's notification preferences"""
    # In a real app, you'd save these to the database
    return {"message": "Notification preferences updated successfully"}