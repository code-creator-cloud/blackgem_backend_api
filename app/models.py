from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    wallet_address = Column(String, nullable=True)
    status = Column(String, default="active")  # "active", "suspended", "inactive"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with transactions
    transactions = relationship("Transaction", back_populates="user")
    # Relationship with deposit addresses
    deposit_addresses = relationship("Web3DepositAddress", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # "deposit" or "withdraw"
    amount = Column(Float, nullable=False)
    currency = Column(String, default="XAF")  # Currency code
    status = Column(String, default="pending")  # "pending", "completed", "failed"
    transaction_hash = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)  # Mobile money transaction ID
    wallet_address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)  # Mobile money phone number
    provider = Column(String, nullable=True)  # "MTN Mobile Money", "Orange Money", etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text, nullable=True)
    
    # Web3 specific fields
    network = Column(String, nullable=True)  # "TRC20", "BEP20"
    deposit_address_id = Column(Integer, ForeignKey("web3_deposit_addresses.id"), nullable=True)

    # Relationship with user
    user = relationship("User", back_populates="transactions") 
    # Relationship with deposit address
    deposit_address = relationship("Web3DepositAddress", back_populates="transactions")

class Web3DepositAddress(Base):
    __tablename__ = "web3_deposit_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address = Column(String, nullable=False, unique=True)
    network = Column(String, nullable=False)  # "TRC20", "BEP20"
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # "pending", "completed", "expired", "cancelled"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="deposit_addresses")
    transactions = relationship("Transaction", back_populates="deposit_address")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin")  # "admin", "super_admin", "moderator"
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    is_active = Column(String, default="active")
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)  # "failed_login", "suspicious_transaction", "unusual_activity"
    severity = Column(String, default="medium")  # "low", "medium", "high", "critical"
    message = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    resolved = Column(String, default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("admins.id"), nullable=True)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String, nullable=False)  # "info", "warning", "error", "security"
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string of additional details
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminNotification(Base):
    __tablename__ = "admin_notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="email")  # "email", "sms", "in_app"
    target_users = Column(Text, nullable=True)  # JSON string of user IDs
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="pending")  # "pending", "sent", "failed"
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 