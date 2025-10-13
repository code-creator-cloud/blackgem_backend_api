from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    balance: float
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    type: str  # "deposit" or "withdraw"
    amount: float
    wallet_address: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    status: str
    transaction_hash: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UnifiedLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str  # "user" or "admin"
    user_data: dict  # User or Admin data
    refresh_token: Optional[str] = None

class AdminResponse(BaseModel):
    id: int
    email: str
    role: str
    permissions: Optional[str] = None
    is_active: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None

# Dashboard schemas
class DashboardData(BaseModel):
    user: UserResponse
    transactions: List[TransactionResponse]
    total_deposits: float
    total_withdrawals: float
    current_balance: float

# AI Assistant schemas
class AIRequest(BaseModel):
    message: str
    context: Optional[str] = None

class AIResponse(BaseModel):
    response: str
    analysis: Optional[str] = None
    recommendations: Optional[List[str]] = None 

# Crypto schemas
class CryptoPrice(BaseModel):
    coin_id: str
    price: float
    timestamp: datetime

class CryptoMarketData(BaseModel):
    name: str
    symbol: str
    current_price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_percentage_24h: float

class InvestmentCalculation(BaseModel):
    coin_id: str
    investment_amount: float
    current_price: float
    coins_purchased: float
    current_value: float
    potential_profit: float

# Payment schemas
class PaymentIntent(BaseModel):
    amount: float
    currency: str = "usd"
    payment_method: str

class PaymentConfirmation(BaseModel):
    payment_intent_id: str
    status: str
    amount: float
    currency: str

class WithdrawalRequest(BaseModel):
    amount: float
    wallet_address: str
    network: str = "TRC20"

class WithdrawalResponse(BaseModel):
    withdrawal_id: str
    amount: float
    wallet_address: str
    status: str
    estimated_completion: str
    network_fee: float

# Email schemas
class EmailNotification(BaseModel):
    user_email: str
    notification_type: str
    subject: str
    message: str

class UserSecurityAlert(BaseModel):
    user_email: str
    alert_type: str
    details: str
    timestamp: datetime

# Mobile Money schemas
class MobileMoneyDeposit(BaseModel):
    phone_number: str
    amount: float
    provider: str = "MTN"  # "MTN" or "Orange"

class MobileMoneyWithdrawal(BaseModel):
    phone_number: str
    amount: float
    provider: str = "MTN"  # "MTN" or "Orange"

class TransactionStatus(BaseModel):
    transaction_id: str
    status: str
    provider: str
    amount: float
    phone_number: str
    created_at: datetime

class MobileMoneyCallback(BaseModel):
    transaction_id: str
    status: str
    provider: str
    amount: float
    phone_number: str
    timestamp: datetime

# Admin schemas
class AdminUser(BaseModel):
    id: int
    email: str
    balance: float
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    transaction_count: int
    total_deposits: float
    total_withdrawals: float
    status: str = "active"

    class Config:
        from_attributes = True

class AdminTransaction(BaseModel):
    id: int
    user_id: int
    user_email: str
    type: str
    amount: float
    currency: str
    status: str
    transaction_hash: Optional[str] = None
    transaction_id: Optional[str] = None
    wallet_address: Optional[str] = None
    phone_number: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class AdminDashboardStats(BaseModel):
    total_users: int
    total_balance: float
    today_transactions: int
    pending_approvals: int
    active_investments: int
    platform_revenue: float
    daily_revenue: float
    weekly_revenue: float
    monthly_revenue: float

class AdminUserList(BaseModel):
    users: List[AdminUser]
    total_count: int
    page: int
    page_size: int

class AdminTransactionList(BaseModel):
    transactions: List[AdminTransaction]
    total_count: int
    page: int
    page_size: int

class AdminUserUpdate(BaseModel):
    status: Optional[str] = None
    balance: Optional[float] = None
    notes: Optional[str] = None

class AdminTransactionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class AdminSystemHealth(BaseModel):
    server_status: str
    database_status: str
    api_response_time: float
    error_rate: float
    active_connections: int

class AdminSecurityAlert(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    created_at: datetime
    resolved: bool = False

class AdminNotification(BaseModel):
    title: str
    message: str
    notification_type: str  # "email", "sms", "in_app"
    target_users: Optional[List[int]] = None  # User IDs, if None sends to all
    scheduled_at: Optional[datetime] = None

class AdminReport(BaseModel):
    report_type: str  # "user_activity", "transactions", "revenue", "security"
    date_from: datetime
    date_to: datetime
    format: str = "json"  # "json", "csv", "pdf"

class AdminSettings(BaseModel):
    platform_name: str
    min_transaction_amount: float
    max_transaction_amount: float
    transaction_fee_percentage: float
    withdrawal_approval_threshold: float
    maintenance_mode: bool = False

# Web3 Schemas
class Web3DepositRequest(BaseModel):
    network: str  # "TRC20" or "BEP20"
    amount: float
    user_wallet_address: Optional[str] = None

class Web3DepositAddressRequest(BaseModel):
    user_id: int
    amount: float
    network: str  # "TRC20" or "BEP20"

class Web3DepositAddressResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    network: str
    address: str
    expires_at: datetime
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Web3DepositAddressStatus(BaseModel):
    id: int
    status: str  # "pending", "completed", "expired", "cancelled"
    amount: float
    network: str
    address: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class Web3DepositResponse(BaseModel):
    deposit_id: int
    network: str
    amount: float
    deposit_address: str
    status: str
    created_at: datetime
    notes: Optional[str] = None

class Web3DepositHistory(BaseModel):
    id: int
    network: str
    amount: float
    currency: str
    status: str
    transaction_hash: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None

class Web3TransactionVerification(BaseModel):
    tx_hash: str
    network: str
    amount: float

class Web3NetworkInfo(BaseModel):
    code: str
    name: str
    currency: str
    decimals: int
    explorer: str
    deposit_address: str
    min_deposit: float
    max_deposit: float

class Web3BalanceResponse(BaseModel):
    network: str
    wallet_address: str
    usdt_balance: float
    usd_equivalent: float

class Web3VerificationResponse(BaseModel):
    verified: bool
    usdt_amount: Optional[float] = None
    usd_amount: Optional[float] = None
    new_balance: Optional[float] = None
    message: str
    error: Optional[str] = None

# Web3 Withdrawal Schemas
class Web3WithdrawalRequest(BaseModel):
    network: str  # "TRC20" or "BEP20"
    amount: float
    wallet_address: str

class Web3WithdrawalResponse(BaseModel):
    withdrawal_id: int
    network: str
    amount: float
    wallet_address: str
    status: str
    transaction_hash: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None

class Web3WithdrawalEligibility(BaseModel):
    eligible: bool
    error: Optional[str] = None
    platform_balance: Optional[float] = None
    withdrawal_fee: Optional[float] = None
    net_amount: Optional[float] = None

class Web3WithdrawalHistory(BaseModel):
    id: int
    network: str
    amount: float
    currency: str
    status: str
    wallet_address: str
    transaction_hash: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None

class Web3PlatformBalance(BaseModel):
    network: str
    platform_balance: float
    currency: str
    last_updated: datetime