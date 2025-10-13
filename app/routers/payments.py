from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app import models, schemas, auth
from app.payment_service import payment_service

router = APIRouter()

@router.post("/create-payment-intent", response_model=Dict)
async def create_payment_intent(
    payment: schemas.PaymentIntent,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a payment intent for deposit"""
    if payment.amount < 10:
        raise HTTPException(status_code=400, detail="Minimum deposit amount is $10")
    
    if payment.amount > 10000:
        raise HTTPException(status_code=400, detail="Maximum deposit amount is $10,000")
    
    payment_data = payment_service.create_payment_intent(payment.amount, current_user.email)
    if not payment_data:
        raise HTTPException(status_code=500, detail="Failed to create payment intent")
    
    return payment_data

@router.post("/confirm-payment", response_model=schemas.PaymentConfirmation)
async def confirm_payment(
    payment_intent_id: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm a payment and create transaction"""
    payment_data = payment_service.confirm_payment(payment_intent_id)
    if not payment_data:
        raise HTTPException(status_code=400, detail="Invalid payment intent")
    
    if payment_data["status"] == "succeeded":
        # Create transaction record
        transaction = models.Transaction(
            user_id=current_user.id,
            type="deposit",
            amount=payment_data["amount"],
            status="completed",
            transaction_hash=payment_intent_id,
            notes=f"Payment confirmed via {payment_data['currency']}"
        )
        db.add(transaction)
        
        # Update user balance
        current_user.balance += payment_data["amount"]
        
        db.commit()
        db.refresh(transaction)
        
        return schemas.PaymentConfirmation(
            payment_intent_id=payment_intent_id,
            status=payment_data["status"],
            amount=payment_data["amount"],
            currency=payment_data["currency"]
        )
    else:
        raise HTTPException(status_code=400, detail=f"Payment failed with status: {payment_data['status']}")

@router.post("/withdrawal", response_model=schemas.WithdrawalResponse)
async def create_withdrawal(
    withdrawal: schemas.WithdrawalRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a withdrawal request"""
    if withdrawal.amount > current_user.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if withdrawal.amount < 5:
        raise HTTPException(status_code=400, detail="Minimum withdrawal amount is $5")
    
    withdrawal_data = payment_service.create_withdrawal_request(
        withdrawal.amount, 
        withdrawal.wallet_address, 
        current_user.email
    )
    
    if not withdrawal_data:
        raise HTTPException(status_code=500, detail="Failed to create withdrawal request")
    
    # Create transaction record
    transaction = models.Transaction(
        user_id=current_user.id,
        type="withdraw",
        amount=withdrawal.amount,
        status="pending",
        wallet_address=withdrawal.wallet_address,
        notes=f"Withdrawal to {withdrawal.network} network"
    )
    db.add(transaction)
    
    # Deduct from user balance
    current_user.balance -= withdrawal.amount
    
    db.commit()
    
    return schemas.WithdrawalResponse(**withdrawal_data)

@router.get("/payment-methods", response_model=Dict)
async def get_payment_methods():
    """Get available payment methods"""
    return payment_service.get_payment_methods()

@router.get("/transaction-status/{transaction_id}")
async def get_transaction_status(
    transaction_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status of a specific transaction"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "transaction_id": transaction.id,
        "type": transaction.type,
        "amount": transaction.amount,
        "status": transaction.status,
        "timestamp": transaction.timestamp,
        "wallet_address": transaction.wallet_address
    }