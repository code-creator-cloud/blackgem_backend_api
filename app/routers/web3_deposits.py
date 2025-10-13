from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
import json

from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user
from app.web3_service import web3_service

router = APIRouter()

@router.post("/deposit/create", response_model=schemas.Web3DepositAddressResponse)
async def create_web3_deposit(
    deposit_request: schemas.Web3DepositAddressRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new Web3 USDT deposit address"""
    
    # Validate network
    if deposit_request.network not in ["TRC20", "BEP20"]:
        raise HTTPException(status_code=400, detail="Invalid network. Must be TRC20 or BEP20")
    
    # Get network info
    network_info = web3_service.get_network_info(deposit_request.network)
    
    # Validate amount
    if deposit_request.amount < network_info.get("min_deposit", 10.0):
        raise HTTPException(
            status_code=400, 
            detail=f"Amount too low. Minimum deposit is {network_info['min_deposit']} USDT"
        )
    
    if deposit_request.amount > network_info.get("max_deposit", 100000.0):
        raise HTTPException(
            status_code=400, 
            detail=f"Amount too high. Maximum deposit is {network_info['max_deposit']} USDT"
        )
    
    # Create deposit address
    deposit_address_data = web3_service.create_deposit_address(
        user_id=current_user.id,
        amount=deposit_request.amount,
        network=deposit_request.network
    )
    
    return schemas.Web3DepositAddressResponse(**deposit_address_data)

@router.get("/deposit/{address_id}/status", response_model=schemas.Web3DepositAddressStatus)
async def get_deposit_address_status(
    address_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the status of a deposit address"""
    try:
        status_data = web3_service.get_deposit_address_status(address_id)
        
        # Verify the address belongs to the current user
        if status_data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return schemas.Web3DepositAddressStatus(**status_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deposit/expire")
async def expire_deposit_addresses():
    """Expire old deposit addresses (admin function)"""
    try:
        expired_count = web3_service.expire_deposit_addresses()
        return {"message": f"Expired {expired_count} deposit addresses"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deposit/verify")
async def verify_web3_deposit(
    verification: schemas.Web3TransactionVerification,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a Web3 deposit transaction"""
    
    # Find the pending deposit
    deposit = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "deposit",
        models.Transaction.status == "pending",
        models.Transaction.provider == verification.network,
        models.Transaction.amount == verification.amount
    ).first()
    
    if not deposit:
        raise HTTPException(status_code=404, detail="No pending deposit found")
    
    # Verify transaction based on network
    if verification.network == "TRC20":
        verification_result = web3_service.verify_transaction_trc20(
            verification.tx_hash,
            verification.amount,
            web3_service.get_deposit_address("TRC20")
        )
    elif verification.network == "BEP20":
        verification_result = web3_service.verify_transaction_bep20(
            verification.tx_hash,
            verification.amount,
            web3_service.get_deposit_address("BEP20")
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid network")
    
    if verification_result["verified"]:
        # Update transaction
        deposit.status = "completed"
        deposit.transaction_hash = verification.tx_hash
        deposit.notes = f"Verified on {verification.network}: {verification_result['amount']} USDT"
        
        # Update user balance
        usd_amount = web3_service.convert_usdt_to_usd(verification_result["amount"])
        current_user.balance += usd_amount
        
        db.commit()
        
        return {
            "verified": True,
            "usdt_amount": verification_result["amount"],
            "usd_amount": usd_amount,
            "new_balance": current_user.balance,
            "message": f"Deposit verified! {verification_result['amount']} USDT = ${usd_amount} USD"
        }
    else:
        return {
            "verified": False,
            "error": verification_result["error"],
            "message": "Transaction verification failed"
        }

@router.get("/networks")
async def get_supported_networks():
    """Get supported Web3 networks"""
    return {
        "networks": [
            {
                "code": "TRC20",
                "name": "Tron Network",
                "currency": "USDT",
                "decimals": 6,
                "explorer": "https://tronscan.org",
                "deposit_address": web3_service.get_deposit_address("TRC20"),
                "min_deposit": 1.0,
                "max_deposit": 100000.0
            },
            {
                "code": "BEP20",
                "name": "Binance Smart Chain",
                "currency": "USDT",
                "decimals": 18,
                "explorer": "https://bscscan.com",
                "deposit_address": web3_service.get_deposit_address("BEP20"),
                "min_deposit": 1.0,
                "max_deposit": 100000.0
            }
        ]
    }

@router.get("/balance/{network}")
async def get_network_balance(
    network: str,
    wallet_address: str,
    current_user: models.User = Depends(get_current_active_user)
):
    """Get USDT balance on specified network"""
    
    if network.upper() == "TRC20":
        balance = web3_service.get_usdt_balance_trc20(wallet_address)
    elif network.upper() == "BEP20":
        balance = web3_service.get_usdt_balance_bep20(wallet_address)
    else:
        raise HTTPException(status_code=400, detail="Invalid network")
    
    return {
        "network": network.upper(),
        "wallet_address": wallet_address,
        "usdt_balance": balance,
        "usd_equivalent": web3_service.convert_usdt_to_usd(balance)
    }

@router.get("/deposits/pending")
async def get_pending_deposits(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's pending Web3 deposits"""
    
    pending_deposits = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "deposit",
        models.Transaction.status == "pending",
        models.Transaction.provider.in_(["TRC20", "BEP20"])
    ).all()
    
    return {
        "pending_deposits": [
            {
                "id": deposit.id,
                "network": deposit.provider,
                "amount": deposit.amount,
                "currency": deposit.currency,
                "status": deposit.status,
                "created_at": deposit.created_at,
                "notes": deposit.notes
            }
            for deposit in pending_deposits
        ]
    }

@router.get("/deposits/history")
async def get_deposit_history(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's Web3 deposit history"""
    
    deposits = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "deposit",
        models.Transaction.provider.in_(["TRC20", "BEP20"])
    ).order_by(models.Transaction.created_at.desc()).all()
    
    return {
        "deposit_history": [
            {
                "id": deposit.id,
                "network": deposit.provider,
                "amount": deposit.amount,
                "currency": deposit.currency,
                "status": deposit.status,
                "transaction_hash": deposit.transaction_hash,
                "created_at": deposit.created_at,
                "notes": deposit.notes
            }
            for deposit in deposits
        ]
    }

# Web3 Withdrawal Endpoints
@router.post("/withdrawal/create", response_model=schemas.Web3WithdrawalResponse)
async def create_web3_withdrawal(
    withdrawal_request: schemas.Web3WithdrawalRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new Web3 USDT withdrawal"""
    
    # Validate network
    if withdrawal_request.network not in ["TRC20", "BEP20"]:
        raise HTTPException(status_code=400, detail="Invalid network. Must be TRC20 or BEP20")
    
    # Get network info
    network_info = web3_service.get_network_info(withdrawal_request.network)
    
    # Check withdrawal eligibility
    eligibility = web3_service.check_withdrawal_eligibility(
        withdrawal_request.network,
        withdrawal_request.amount,
        current_user.balance
    )
    
    if not eligibility["eligible"]:
        raise HTTPException(status_code=400, detail=eligibility["error"])
    
    # Calculate withdrawal fee
    withdrawal_fee = network_info.get("withdrawal_fee", 1.0)
    net_amount = withdrawal_request.amount - withdrawal_fee
    
    # Create transaction record
    transaction = models.Transaction(
        user_id=current_user.id,
        type="withdrawal",
        amount=withdrawal_request.amount,
        currency="USDT",
        status="pending",
        provider=withdrawal_request.network,
        wallet_address=withdrawal_request.wallet_address,
        description=f"USDT withdrawal on {withdrawal_request.network} network",
        notes=f"Withdrawal fee: {withdrawal_fee} USDT, Net amount: {net_amount} USDT"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return schemas.Web3WithdrawalResponse(
        withdrawal_id=transaction.id,
        network=withdrawal_request.network,
        amount=withdrawal_request.amount,
        wallet_address=withdrawal_request.wallet_address,
        status=transaction.status,
        created_at=transaction.created_at,
        notes=f"Withdrawal fee: {withdrawal_fee} USDT, Net amount: {net_amount} USDT"
    )

@router.post("/withdrawal/process/{withdrawal_id}")
async def process_web3_withdrawal(
    withdrawal_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process a pending Web3 withdrawal"""
    
    # Find the withdrawal transaction
    withdrawal = db.query(models.Transaction).filter(
        models.Transaction.id == withdrawal_id,
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "withdrawal",
        models.Transaction.status == "pending"
    ).first()
    
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found or already processed")
    
    # Check eligibility again
    eligibility = web3_service.check_withdrawal_eligibility(
        withdrawal.provider,
        withdrawal.amount,
        current_user.balance
    )
    
    if not eligibility["eligible"]:
        withdrawal.status = "failed"
        withdrawal.notes = f"Processing failed: {eligibility['error']}"
        db.commit()
        raise HTTPException(status_code=400, detail=eligibility["error"])
    
    try:
        # Send USDT based on network
        if withdrawal.provider == "TRC20":
            result = web3_service.send_usdt_trc20(
                withdrawal.wallet_address,
                withdrawal.amount
            )
        elif withdrawal.provider == "BEP20":
            result = web3_service.send_usdt_bep20(
                withdrawal.wallet_address,
                withdrawal.amount
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid network")
        
        if result["success"]:
            # Update transaction
            withdrawal.status = "completed"
            withdrawal.transaction_hash = result["tx_hash"]
            withdrawal.notes = f"Withdrawal completed on {result['network']}"
            
            # Update user balance
            current_user.balance -= withdrawal.amount
            
            db.commit()
            
            return {
                "success": True,
                "withdrawal_id": withdrawal.id,
                "tx_hash": result["tx_hash"],
                "amount": result["amount"],
                "network": result["network"],
                "new_balance": current_user.balance,
                "message": f"Withdrawal successful! {result['amount']} USDT sent to {withdrawal.wallet_address}"
            }
        else:
            # Update transaction status
            withdrawal.status = "failed"
            withdrawal.notes = f"Withdrawal failed: {result['error']}"
            db.commit()
            
            raise HTTPException(status_code=400, detail=f"Withdrawal failed: {result['error']}")
            
    except Exception as e:
        withdrawal.status = "failed"
        withdrawal.notes = f"Processing error: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Withdrawal processing error: {str(e)}")

@router.get("/withdrawal/eligibility")
async def check_withdrawal_eligibility(
    network: str,
    amount: float,
    current_user: models.User = Depends(get_current_active_user)
):
    """Check if user can withdraw the specified amount"""
    
    if network not in ["TRC20", "BEP20"]:
        raise HTTPException(status_code=400, detail="Invalid network")
    
    eligibility = web3_service.check_withdrawal_eligibility(network, amount, current_user.balance)
    network_info = web3_service.get_network_info(network)
    
    return schemas.Web3WithdrawalEligibility(
        eligible=eligibility["eligible"],
        error=eligibility.get("error"),
        platform_balance=eligibility.get("platform_balance"),
        withdrawal_fee=network_info.get("withdrawal_fee"),
        net_amount=amount - network_info.get("withdrawal_fee", 0) if eligibility["eligible"] else None
    )

@router.get("/withdrawal/history")
async def get_withdrawal_history(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's Web3 withdrawal history"""
    
    withdrawals = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "withdrawal",
        models.Transaction.provider.in_(["TRC20", "BEP20"])
    ).order_by(models.Transaction.created_at.desc()).all()
    
    return {
        "withdrawal_history": [
            {
                "id": withdrawal.id,
                "network": withdrawal.provider,
                "amount": withdrawal.amount,
                "currency": withdrawal.currency,
                "status": withdrawal.status,
                "wallet_address": withdrawal.wallet_address,
                "transaction_hash": withdrawal.transaction_hash,
                "created_at": withdrawal.created_at,
                "notes": withdrawal.notes
            }
            for withdrawal in withdrawals
        ]
    }

@router.get("/platform/balance/{network}")
async def get_platform_balance(
    network: str,
    current_user: models.User = Depends(get_current_active_user)
):
    """Get platform USDT balance on specified network (admin only)"""
    
    if network.upper() == "TRC20":
        balance = web3_service.get_platform_balance_trc20()
    elif network.upper() == "BEP20":
        balance = web3_service.get_platform_balance_bep20()
    else:
        raise HTTPException(status_code=400, detail="Invalid network")
    
    return schemas.Web3PlatformBalance(
        network=network.upper(),
        platform_balance=balance,
        currency="USDT",
        last_updated=datetime.now()
    ) 