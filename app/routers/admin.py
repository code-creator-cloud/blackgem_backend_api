from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel

from app.database import get_db
from app import models, schemas
from app.admin_auth import get_current_admin, get_current_super_admin, check_permission, get_password_hash, create_access_token, verify_password
from app.schemas import Token

router = APIRouter()

# Admin Authentication - Now handled by unified login endpoint
# The /api/users/login endpoint now handles both users and admins

# Dashboard Statistics
@router.get("/dashboard/stats", response_model=schemas.AdminDashboardStats)
async def get_dashboard_stats(
    current_admin: models.Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Get total users
    total_users = db.query(models.User).count()
    
    # Get total balance
    total_balance = db.query(func.sum(models.User.balance)).scalar() or 0
    
    # Get today's transactions
    today = datetime.utcnow().date()
    today_transactions = db.query(models.Transaction).filter(
        func.date(models.Transaction.created_at) == today
    ).count()
    
    # Get pending approvals
    pending_approvals = db.query(models.Transaction).filter(
        models.Transaction.status == "pending"
    ).count()
    
    # Get active investments (users with balance > 0)
    active_investments = db.query(models.User).filter(models.User.balance > 0).count()
    
    # Calculate revenue (transaction fees)
    # This is a simplified calculation - you might want to track actual fees
    transaction_fee_percentage = float(os.getenv("TRANSACTION_FEE_PERCENTAGE", "0.02"))  # 2% default
    platform_revenue = total_balance * transaction_fee_percentage
    
    # Calculate daily, weekly, monthly revenue
    daily_revenue = platform_revenue / 30  # Simplified
    weekly_revenue = platform_revenue / 4
    monthly_revenue = platform_revenue
    
    return schemas.AdminDashboardStats(
        total_users=total_users,
        total_balance=total_balance,
        today_transactions=today_transactions,
        pending_approvals=pending_approvals,
        active_investments=active_investments,
        platform_revenue=platform_revenue,
        daily_revenue=daily_revenue,
        weekly_revenue=weekly_revenue,
        monthly_revenue=monthly_revenue
    )

# User Management
@router.get("/users", response_model=schemas.AdminUserList)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_admin: models.Admin = Depends(check_permission("user_management")),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)
    
    if search:
        query = query.filter(
            or_(
                models.User.email.contains(search),
                models.User.wallet_address.contains(search)
            )
        )
    
    if status_filter:
        valid_statuses = ["active", "suspended", "inactive"]
        if status_filter not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        query = query.filter(models.User.status == status_filter)
    
    total_count = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Convert to AdminUser format with simplified statistics
    admin_users = []
    for user in users:
        # Get user statistics (simplified approach)
        transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user.id).all()
        total_deposits = sum(t.amount for t in transactions if t.type == "deposit" and t.status == "completed")
        total_withdrawals = sum(t.amount for t in transactions if t.type == "withdraw" and t.status == "completed")
        
        admin_users.append(schemas.AdminUser(
            id=user.id,
            email=user.email,
            balance=user.balance,
            wallet_address=user.wallet_address,
            created_at=user.created_at,
            updated_at=user.updated_at,
            transaction_count=len(transactions),
            total_deposits=total_deposits,
            total_withdrawals=total_withdrawals,
            status=user.status
        ))
    
    return schemas.AdminUserList(
        users=admin_users,
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.get("/users/{user_id}", response_model=schemas.AdminUser)
async def get_user(
    user_id: int,
    current_admin: models.Admin = Depends(check_permission("user_management")),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user statistics (simplified approach)
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user.id).all()
    total_deposits = sum(t.amount for t in transactions if t.type == "deposit" and t.status == "completed")
    total_withdrawals = sum(t.amount for t in transactions if t.type == "withdraw" and t.status == "completed")
    transaction_count = len(transactions)
    
    return schemas.AdminUser(
        id=user.id,
        email=user.email,
        balance=user.balance,
        wallet_address=user.wallet_address,
        created_at=user.created_at,
        updated_at=user.updated_at,
        transaction_count=transaction_count,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        status=user.status
    )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    current_admin: models.Admin = Depends(check_permission("user_management")),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.balance is not None:
        user.balance = user_update.balance
    
    try:
        # Add notes to transaction log
        if user_update.notes:
            log = models.SystemLog(
                log_type="info",
                message=f"Admin {current_admin.email} updated user {user.email}",
                details=json.dumps({"notes": user_update.notes}),
                admin_id=current_admin.id,
                user_id=user.id
            )
            db.add(log)
        
        db.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

# Transaction Management
@router.get("/transactions", response_model=schemas.AdminTransactionList)
async def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    user_id: Optional[int] = None,
    current_admin: models.Admin = Depends(check_permission("transaction_management")),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction)
    
    if type_filter:
        valid_types = ["deposit", "withdraw"]
        if type_filter not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {valid_types}")
        query = query.filter(models.Transaction.type == type_filter)
    
    if status_filter:
        valid_statuses = ["pending", "completed", "failed"]
        if status_filter not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        query = query.filter(models.Transaction.status == status_filter)
    
    if user_id:
        query = query.filter(models.Transaction.user_id == user_id)
    
    total_count = query.count()
    transactions = query.order_by(models.Transaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Get user emails efficiently
    user_ids = [t.user_id for t in transactions]
    users = db.query(models.User.id, models.User.email).filter(models.User.id.in_(user_ids)).all()
    user_emails = {user.id: user.email for user in users}
    
    # Convert to AdminTransaction format
    admin_transactions = []
    for transaction in transactions:
        admin_transactions.append(schemas.AdminTransaction(
            id=transaction.id,
            user_id=transaction.user_id,
            user_email=user_emails.get(transaction.user_id, "Unknown"),
            type=transaction.type,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            transaction_hash=transaction.transaction_hash,
            transaction_id=transaction.transaction_id,
            wallet_address=transaction.wallet_address,
            phone_number=transaction.phone_number,
            provider=transaction.provider,
            description=transaction.description,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            notes=transaction.notes
        ))
    
    return schemas.AdminTransactionList(
        transactions=admin_transactions,
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    transaction_update: schemas.AdminTransactionUpdate,
    current_admin: models.Admin = Depends(check_permission("transaction_management")),
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction_update.status:
        valid_statuses = ["pending", "completed", "failed"]
        if transaction_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        transaction.status = transaction_update.status
    
    if transaction_update.notes:
        transaction.notes = transaction_update.notes
    
    try:
        # Log the update
        log = models.SystemLog(
            log_type="info",
            message=f"Admin {current_admin.email} updated transaction {transaction_id}",
            details=json.dumps({"status": transaction_update.status, "notes": transaction_update.notes}),
            admin_id=current_admin.id
        )
        db.add(log)
        
        db.commit()
        return {"message": "Transaction updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

# System Health
@router.get("/system/health", response_model=schemas.AdminSystemHealth)
async def get_system_health(
    current_admin: models.Admin = Depends(check_permission("system_monitoring")),
    db: Session = Depends(get_db)
):
    # This is a simplified health check - in production you'd want more comprehensive monitoring
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception as e:
        database_status = "unhealthy"
    
    return schemas.AdminSystemHealth(
        server_status="healthy",
        database_status=database_status,
        api_response_time=0.15,  # Mock value
        error_rate=0.01,  # Mock value
        active_connections=42  # Mock value
    )

# Security Alerts
@router.get("/security/alerts", response_model=List[schemas.AdminSecurityAlert])
async def get_security_alerts(
    current_admin: models.Admin = Depends(check_permission("security_monitoring")),
    db: Session = Depends(get_db)
):
    alerts = db.query(models.SecurityAlert).filter(
        models.SecurityAlert.resolved == "false"
    ).order_by(models.SecurityAlert.created_at.desc()).all()
    
    return [
        schemas.AdminSecurityAlert(
            id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            user_id=alert.user_id,
            user_email=None,  # You'd need to join with User table
            created_at=alert.created_at,
            resolved=alert.resolved == "true"
        )
        for alert in alerts
    ]

@router.put("/security/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: int,
    current_admin: models.Admin = Depends(check_permission("security_monitoring")),
    db: Session = Depends(get_db)
):
    alert = db.query(models.SecurityAlert).filter(models.SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    try:
        alert.resolved = "true"
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_admin.id
        
        db.commit()
        return {"message": "Alert resolved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

# Notifications
@router.post("/notifications")
async def create_notification(
    notification: schemas.AdminNotification,
    current_admin: models.Admin = Depends(check_permission("notifications")),
    db: Session = Depends(get_db)
):
    db_notification = models.AdminNotification(
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        target_users=json.dumps(notification.target_users) if notification.target_users else None,
        scheduled_at=notification.scheduled_at,
        created_by=current_admin.id
    )
    
    try:
        db.add(db_notification)
        db.commit()
        
        return {"message": "Notification created successfully", "id": db_notification.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

# Reports
@router.post("/reports/generate")
async def generate_report(
    report: schemas.AdminReport,
    current_admin: models.Admin = Depends(check_permission("reports")),
    db: Session = Depends(get_db)
):
    # This is a simplified report generation - you'd want more comprehensive reporting
    if report.report_type == "user_activity":
        data = db.query(models.User).filter(
            models.User.created_at >= report.date_from,
            models.User.created_at <= report.date_to
        ).all()
    elif report.report_type == "transactions":
        data = db.query(models.Transaction).filter(
            models.Transaction.created_at >= report.date_from,
            models.Transaction.created_at <= report.date_to
        ).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    return {
        "message": "Report generated successfully",
        "report_type": report.report_type,
        "data_count": len(data),
        "format": report.format
    }

# Admin Management (Super Admin only)
@router.post("/admins")
async def create_admin(
    email: str,
    password: str,
    role: str = "admin",
    permissions: Optional[List[str]] = None,
    current_admin: models.Admin = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    # Check if admin already exists
    existing_admin = db.query(models.Admin).filter(models.Admin.email == email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    hashed_password = get_password_hash(password)
    
    new_admin = models.Admin(
        email=email,
        hashed_password=hashed_password,
        role=role,
        permissions=json.dumps(permissions) if permissions else None
    )
    
    try:
        db.add(new_admin)
        db.commit()
        
        return {"message": "Admin created successfully", "id": new_admin.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred") 

# Analytics and Reports
@router.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_admin: models.Admin = Depends(check_permission("reports")),
    db: Session = Depends(get_db)
):
    """Get revenue analytics for different periods"""
    end_date = datetime.utcnow()
    
    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:  # 1y
        start_date = end_date - timedelta(days=365)
    
    # Get transactions in the period
    transactions = db.query(models.Transaction).filter(
        models.Transaction.created_at >= start_date,
        models.Transaction.created_at <= end_date,
        models.Transaction.status == "completed"
    ).all()
    
    # Calculate revenue by type
    deposits = [t for t in transactions if t.type == "deposit"]
    withdrawals = [t for t in transactions if t.type == "withdraw"]
    
    total_deposits = sum(t.amount for t in deposits)
    total_withdrawals = sum(t.amount for t in withdrawals)
    
    # Calculate fees (simplified - you might want to track actual fees)
    transaction_fee_percentage = float(os.getenv("TRANSACTION_FEE_PERCENTAGE", "0.02"))  # 2% default
    revenue = total_deposits * transaction_fee_percentage
    
    return {
        "period": period,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "revenue": revenue,
        "transaction_count": len(transactions),
        "deposit_count": len(deposits),
        "withdrawal_count": len(withdrawals)
    }

@router.get("/analytics/user-growth")
async def get_user_growth_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_admin: models.Admin = Depends(check_permission("reports")),
    db: Session = Depends(get_db)
):
    """Get user growth analytics"""
    end_date = datetime.utcnow()
    
    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:  # 1y
        start_date = end_date - timedelta(days=365)
    
    # Get new users in the period
    new_users = db.query(models.User).filter(
        models.User.created_at >= start_date,
        models.User.created_at <= end_date
    ).count()
    
    # Get total users before the period
    total_before = db.query(models.User).filter(
        models.User.created_at < start_date
    ).count()
    
    # Get total users now
    total_now = db.query(models.User).count()
    
    growth_rate = ((total_now - total_before) / total_before * 100) if total_before > 0 else 0
    
    return {
        "period": period,
        "new_users": new_users,
        "total_users": total_now,
        "growth_rate": round(growth_rate, 2),
        "start_date": start_date,
        "end_date": end_date
    }

# Mobile Money Management
@router.get("/mobile-money/status")
async def get_mobile_money_status(
    current_admin: models.Admin = Depends(check_permission("system_monitoring")),
    db: Session = Depends(get_db)
):
    """Get mobile money integration status"""
    # Get recent mobile money transactions
    recent_transactions = db.query(models.Transaction).filter(
        models.Transaction.provider.isnot(None)
    ).order_by(models.Transaction.created_at.desc()).limit(10).all()
    
    # Calculate success rates
    total_mobile = db.query(models.Transaction).filter(
        models.Transaction.provider.isnot(None)
    ).count()
    
    successful_mobile = db.query(models.Transaction).filter(
        models.Transaction.provider.isnot(None),
        models.Transaction.status == "completed"
    ).count()
    
    success_rate = (successful_mobile / total_mobile * 100) if total_mobile > 0 else 0
    
    # Get provider breakdown
    mtn_transactions = db.query(models.Transaction).filter(
        models.Transaction.provider == "MTN Mobile Money"
    ).count()
    
    orange_transactions = db.query(models.Transaction).filter(
        models.Transaction.provider == "Orange Money"
    ).count()
    
    return {
        "total_mobile_transactions": total_mobile,
        "successful_transactions": successful_mobile,
        "success_rate": round(success_rate, 2),
        "mtn_transactions": mtn_transactions,
        "orange_transactions": orange_transactions,
        "recent_transactions": [
            {
                "id": t.id,
                "type": t.type,
                "amount": t.amount,
                "status": t.status,
                "provider": t.provider,
                "phone_number": t.phone_number,
                "created_at": t.created_at
            }
            for t in recent_transactions
        ]
    }

# AI Assistant Monitoring
@router.get("/ai/analytics")
async def get_ai_analytics(
    current_admin: models.Admin = Depends(check_permission("system_monitoring")),
    db: Session = Depends(get_db)
):
    """Get AI assistant usage analytics"""
    # This would typically come from AI service logs
    # For now, we'll return mock data
    return {
        "total_conversations": 1247,
        "average_response_time": 2.3,
        "user_satisfaction": 4.2,
        "common_topics": [
            {"topic": "Investment Advice", "count": 456},
            {"topic": "Account Issues", "count": 234},
            {"topic": "Transaction Help", "count": 189},
            {"topic": "General Questions", "count": 156}
        ],
        "daily_usage": [
            {"date": "2024-01-01", "conversations": 45},
            {"date": "2024-01-02", "conversations": 52},
            {"date": "2024-01-03", "conversations": 38},
            {"date": "2024-01-04", "conversations": 61},
            {"date": "2024-01-05", "conversations": 49}
        ]
    }

# System Logs
@router.get("/system/logs")
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    log_type: Optional[str] = None,
    current_admin: models.Admin = Depends(check_permission("system_monitoring")),
    db: Session = Depends(get_db)
):
    """Get system logs"""
    query = db.query(models.SystemLog)
    
    if log_type:
        query = query.filter(models.SystemLog.log_type == log_type)
    
    total_count = query.count()
    logs = query.order_by(models.SystemLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "log_type": log.log_type,
                "message": log.message,
                "details": log.details,
                "admin_id": log.admin_id,
                "user_id": log.user_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ],
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }

# Bulk Operations
@router.post("/users/bulk-action")
async def bulk_user_action(
    user_ids: List[int],
    action: str,  # "suspend", "activate", "delete"
    current_admin: models.Admin = Depends(check_permission("user_management")),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on users"""
    if action not in ["suspend", "activate", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    
    for user in users:
        if action == "suspend":
            user.status = "suspended"
        elif action == "activate":
            user.status = "active"
        elif action == "delete":
            user.status = "inactive"  # Soft delete
    
    try:
        # Log the bulk action
        log = models.SystemLog(
            log_type="info",
            message=f"Admin {current_admin.email} performed bulk action '{action}' on {len(users)} users",
            details=json.dumps({"action": action, "user_ids": user_ids}),
            admin_id=current_admin.id
        )
        db.add(log)
        
        db.commit()
        
        return {"message": f"Bulk action '{action}' completed on {len(users)} users"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

# Export Data
@router.get("/export/users")
async def export_users(
    format: str = Query("json", regex="^(json|csv)$"),
    current_admin: models.Admin = Depends(check_permission("reports")),
    db: Session = Depends(get_db)
):
    """Export user data"""
    users = db.query(models.User).all()
    
    if format == "json":
        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "balance": user.balance,
                    "wallet_address": user.wallet_address,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                for user in users
            ]
        }
    else:  # csv
        # You would implement CSV export here
        return {"message": "CSV export not implemented yet"}