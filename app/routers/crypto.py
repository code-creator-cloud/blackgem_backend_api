from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime

from app.database import get_db
from app import models, schemas, auth
from app.crypto_service import crypto_service

router = APIRouter()

@router.get("/prices", response_model=Dict[str, float])
async def get_crypto_prices():
    """Get current prices for all supported cryptocurrencies"""
    prices = crypto_service.get_crypto_prices()
    if not prices:
        raise HTTPException(status_code=500, detail="Failed to fetch crypto prices")
    return prices

@router.get("/price/{coin_id}")
async def get_crypto_price(coin_id: str):
    """Get current price for a specific cryptocurrency"""
    price = crypto_service.get_crypto_price(coin_id)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Price not found for {coin_id}")
    return {"coin_id": coin_id, "price": price, "timestamp": datetime.utcnow()}

@router.get("/market-data/{coin_id}", response_model=schemas.CryptoMarketData)
async def get_crypto_market_data(coin_id: str):
    """Get detailed market data for a cryptocurrency"""
    market_data = crypto_service.get_crypto_market_data(coin_id)
    if not market_data:
        raise HTTPException(status_code=404, detail=f"Market data not found for {coin_id}")
    return market_data

@router.post("/calculate-investment", response_model=schemas.InvestmentCalculation)
async def calculate_investment(
    coin_id: str,
    amount: float,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Calculate investment value and potential returns"""
    calculation = crypto_service.calculate_investment_value(coin_id, amount)
    if not calculation:
        raise HTTPException(status_code=400, detail=f"Could not calculate investment for {coin_id}")
    return calculation

@router.get("/portfolio-value")
async def get_portfolio_value(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate total portfolio value based on user's transactions"""
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.status == "completed"
    ).all()
    
    total_invested = sum(t.amount for t in transactions if t.type == "deposit")
    total_withdrawn = sum(t.amount for t in transactions if t.type == "withdraw")
    net_investment = total_invested - total_withdrawn
    
    # Simulate portfolio growth (in real app, you'd track actual crypto holdings)
    estimated_growth = net_investment * 0.15  # 15% estimated growth
    current_value = net_investment + estimated_growth
    
    return {
        "total_invested": total_invested,
        "total_withdrawn": total_withdrawn,
        "net_investment": net_investment,
        "estimated_growth": estimated_growth,
        "current_value": current_value,
        "growth_percentage": (estimated_growth / net_investment * 100) if net_investment > 0 else 0
    }