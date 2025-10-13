from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..models import User, Transaction
from ..schemas import MobileMoneyDeposit, MobileMoneyWithdrawal, TransactionStatus
from ..auth import get_current_user
from ..mobile_money_service import mobile_money_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile-money", tags=["Mobile Money"])

@router.post("/deposit/mtn")
async def initiate_mtn_deposit(
    deposit_data: MobileMoneyDeposit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate MTN Mobile Money deposit"""
    try:
        # Validate phone number
        if not mobile_money_service.validate_phone_number(deposit_data.phone_number, "MTN"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MTN phone number format"
            )
        
        # Validate amount
        if not mobile_money_service.validate_amount(deposit_data.amount, "deposit"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deposit amount. Must be between 100 and 500,000 XAF"
            )
        
        # Initiate deposit
        result = await mobile_money_service.initiate_mtn_deposit(
            phone_number=deposit_data.phone_number,
            amount=deposit_data.amount,
            user_id=current_user.id
        )
        
        if result["success"]:
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id,
                type="deposit",
                amount=deposit_data.amount,
                currency="XAF",
                provider="MTN Mobile Money",
                status="pending",
                transaction_id=result["transaction_id"],
                phone_number=deposit_data.phone_number,
                description=f"MTN Mobile Money deposit of {deposit_data.amount} XAF"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            return {
                "success": True,
                "message": "MTN Mobile Money deposit initiated successfully",
                "transaction_id": result["transaction_id"],
                "amount": deposit_data.amount,
                "phone_number": deposit_data.phone_number,
                "status": "pending"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN deposit error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate MTN deposit"
        )

@router.post("/deposit/orange")
async def initiate_orange_deposit(
    deposit_data: MobileMoneyDeposit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate Orange Money deposit"""
    try:
        # Validate phone number
        if not mobile_money_service.validate_phone_number(deposit_data.phone_number, "Orange"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Orange phone number format"
            )
        
        # Validate amount
        if not mobile_money_service.validate_amount(deposit_data.amount, "deposit"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deposit amount. Must be between 100 and 500,000 XAF"
            )
        
        # Initiate deposit
        result = await mobile_money_service.initiate_orange_deposit(
            phone_number=deposit_data.phone_number,
            amount=deposit_data.amount,
            user_id=current_user.id
        )
        
        if result["success"]:
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id,
                type="deposit",
                amount=deposit_data.amount,
                currency="XAF",
                provider="Orange Money",
                status="pending",
                transaction_id=result["transaction_id"],
                phone_number=deposit_data.phone_number,
                description=f"Orange Money deposit of {deposit_data.amount} XAF"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            return {
                "success": True,
                "message": "Orange Money deposit initiated successfully",
                "transaction_id": result["transaction_id"],
                "amount": deposit_data.amount,
                "phone_number": deposit_data.phone_number,
                "status": "pending"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orange deposit error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Orange deposit"
        )

@router.post("/withdrawal/mtn")
async def initiate_mtn_withdrawal(
    withdrawal_data: MobileMoneyWithdrawal,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate MTN Mobile Money withdrawal"""
    try:
        # Check if user has sufficient balance
        if current_user.balance < withdrawal_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for withdrawal"
            )
        
        # Validate phone number
        if not mobile_money_service.validate_phone_number(withdrawal_data.phone_number, "MTN"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MTN phone number format"
            )
        
        # Validate amount
        if not mobile_money_service.validate_amount(withdrawal_data.amount, "withdrawal"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid withdrawal amount. Must be between 100 and 500,000 XAF"
            )
        
        # Initiate withdrawal
        result = await mobile_money_service.initiate_mtn_withdrawal(
            phone_number=withdrawal_data.phone_number,
            amount=withdrawal_data.amount,
            user_id=current_user.id
        )
        
        if result["success"]:
            # Deduct from user balance
            current_user.balance -= withdrawal_data.amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id,
                type="withdrawal",
                amount=withdrawal_data.amount,
                currency="XAF",
                provider="MTN Mobile Money",
                status="pending",
                transaction_id=result["transaction_id"],
                phone_number=withdrawal_data.phone_number,
                description=f"MTN Mobile Money withdrawal of {withdrawal_data.amount} XAF"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            return {
                "success": True,
                "message": "MTN Mobile Money withdrawal initiated successfully",
                "transaction_id": result["transaction_id"],
                "amount": withdrawal_data.amount,
                "phone_number": withdrawal_data.phone_number,
                "status": "pending"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN withdrawal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate MTN withdrawal"
        )

@router.post("/withdrawal/orange")
async def initiate_orange_withdrawal(
    withdrawal_data: MobileMoneyWithdrawal,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate Orange Money withdrawal"""
    try:
        # Check if user has sufficient balance
        if current_user.balance < withdrawal_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for withdrawal"
            )
        
        # Validate phone number
        if not mobile_money_service.validate_phone_number(withdrawal_data.phone_number, "Orange"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Orange phone number format"
            )
        
        # Validate amount
        if not mobile_money_service.validate_amount(withdrawal_data.amount, "withdrawal"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid withdrawal amount. Must be between 100 and 500,000 XAF"
            )
        
        # Initiate withdrawal
        result = await mobile_money_service.initiate_orange_withdrawal(
            phone_number=withdrawal_data.phone_number,
            amount=withdrawal_data.amount,
            user_id=current_user.id
        )
        
        if result["success"]:
            # Deduct from user balance
            current_user.balance -= withdrawal_data.amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id,
                type="withdrawal",
                amount=withdrawal_data.amount,
                currency="XAF",
                provider="Orange Money",
                status="pending",
                transaction_id=result["transaction_id"],
                phone_number=withdrawal_data.phone_number,
                description=f"Orange Money withdrawal of {withdrawal_data.amount} XAF"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            return {
                "success": True,
                "message": "Orange Money withdrawal initiated successfully",
                "transaction_id": result["transaction_id"],
                "amount": withdrawal_data.amount,
                "phone_number": withdrawal_data.phone_number,
                "status": "pending"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orange withdrawal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Orange withdrawal"
        )

@router.get("/transaction/{transaction_id}")
async def get_transaction_status(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of a mobile money transaction"""
    try:
        # Check if transaction exists in database
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Get status from mobile money service
        status_result = await mobile_money_service.check_transaction_status(transaction_id)
        
        if status_result["success"]:
            # Update transaction status in database
            transaction.status = status_result["status"]
            db.commit()
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": status_result["status"],
                "provider": status_result["provider"],
                "type": status_result["type"],
                "amount": status_result["amount"],
                "phone_number": status_result["phone_number"],
                "created_at": status_result["created_at"]
            }
        else:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": transaction.status,
                "error": status_result["error"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transaction status"
        )

@router.get("/transactions")
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Get user's mobile money transactions"""
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.provider.in_(["MTN Mobile Money", "Orange Money"])
        ).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "transactions": [
                {
                    "id": t.id,
                    "transaction_id": t.transaction_id,
                    "type": t.type,
                    "amount": t.amount,
                    "currency": t.currency,
                    "provider": t.provider,
                    "status": t.status,
                    "phone_number": t.phone_number,
                    "description": t.description,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ],
            "total": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"Get transactions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )

@router.post("/callback/mtn")
async def mtn_callback(callback_data: Dict):
    """Handle MTN Mobile Money callback"""
    try:
        result = await mobile_money_service.process_callback("MTN", callback_data)
        return result
    except Exception as e:
        logger.error(f"MTN callback error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/callback/orange")
async def orange_callback(callback_data: Dict):
    """Handle Orange Money callback"""
    try:
        result = await mobile_money_service.process_callback("Orange", callback_data)
        return result
    except Exception as e:
        logger.error(f"Orange callback error: {str(e)}")
        return {"success": False, "error": str(e)} 