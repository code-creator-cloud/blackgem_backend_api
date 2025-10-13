from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas, auth

router = APIRouter()

@router.post("/chat", response_model=schemas.AIResponse)
async def chat_with_ai(
    request: schemas.AIRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enhanced AI chat with investment analysis"""
    # Get user's transaction history
    user_transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()
    
    # Calculate advanced metrics
    total_deposits = sum(t.amount for t in user_transactions if t.type == "deposit" and t.status == "completed")
    total_withdrawals = sum(t.amount for t in user_transactions if t.type == "withdraw" and t.status == "completed")
    recent_transactions = [t for t in user_transactions if t.timestamp > datetime.utcnow() - timedelta(days=30)]
    
    # Advanced AI analysis based on user message
    message_lower = request.message.lower()
    
    if "risk" in message_lower or "safety" in message_lower:
        response = f"Based on your ${total_deposits:.2f} in deposits, your risk profile appears moderate. Consider diversifying across different investment types."
        analysis = "Risk assessment completed. User shows balanced investment approach."
        recommendations = [
            "Consider 60% stable investments, 30% growth, 10% high-risk",
            "Set up automatic rebalancing",
            "Monitor market volatility indicators"
        ]
    
    elif "growth" in message_lower or "profit" in message_lower:
        growth_rate = ((total_deposits - total_withdrawals) / total_deposits * 100) if total_deposits > 0 else 0
        response = f"Your portfolio shows a {growth_rate:.1f}% growth rate. For better returns, consider compound interest strategies."
        analysis = "Growth analysis indicates positive trajectory with room for optimization."
        recommendations = [
            "Increase monthly investment by 10%",
            "Explore compound interest opportunities",
            "Consider long-term investment vehicles"
        ]
    
    elif "market" in message_lower or "trend" in message_lower:
        response = "Current market analysis suggests cryptocurrency volatility. Consider dollar-cost averaging for stable growth."
        analysis = "Market trend analysis completed with volatility considerations."
        recommendations = [
            "Implement dollar-cost averaging strategy",
            "Diversify across multiple cryptocurrencies",
            "Set up price alerts for major movements"
        ]
    
    else:
        response = "I can help with risk assessment, growth analysis, market trends, and investment strategies. What specific area would you like to explore?"
        analysis = "General inquiry - providing guidance on available AI features."
        recommendations = [
            "Ask about risk assessment",
            "Request growth analysis",
            "Get market trend insights"
        ]
        
        return schemas.AIResponse(
            response=response,
        analysis=analysis,
        recommendations=recommendations
    )

@router.get("/portfolio-analysis", response_model=schemas.AIResponse)
async def get_portfolio_analysis(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Advanced portfolio analysis with AI insights"""
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()
    
    # Calculate portfolio metrics
    total_invested = sum(t.amount for t in transactions if t.type == "deposit" and t.status == "completed")
    total_withdrawn = sum(t.amount for t in transactions if t.type == "withdraw" and t.status == "completed")
    net_position = total_invested - total_withdrawn
    growth_rate = ((net_position - total_withdrawn) / total_invested * 100) if total_invested > 0 else 0
    
    # AI portfolio assessment
    if growth_rate > 10:
        assessment = "Excellent portfolio performance with strong growth trajectory."
        risk_level = "Moderate"
        strategy = "Continue current strategy with slight optimization"
    elif growth_rate > 0:
        assessment = "Good portfolio performance with positive growth."
        risk_level = "Conservative"
        strategy = "Consider increasing investment frequency"
    else:
        assessment = "Portfolio needs optimization for better returns."
        risk_level = "High"
        strategy = "Implement risk management strategies"
    
    response = f"Portfolio Analysis: Net Position ${net_position:.2f}, Growth Rate {growth_rate:.1f}%, Risk Level: {risk_level}"
    analysis = f"AI Assessment: {assessment} Recommended Strategy: {strategy}"
    recommendations = [
        "Diversify across 3-5 different cryptocurrencies",
        "Set up automatic investment schedules",
        "Monitor portfolio performance weekly",
        "Consider professional financial advice"
    ]
    
    return schemas.AIResponse(
        response=response,
        analysis=analysis,
        recommendations=recommendations
    )

@router.get("/market-prediction", response_model=schemas.AIResponse)
async def get_market_prediction(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI-powered market prediction based on user's investment pattern"""
    # Simulate AI market prediction
    response = "Market Prediction: Based on current trends, expect 15-25% volatility in the next 30 days. Bitcoin showing bullish signals."
    analysis = "AI analysis indicates favorable market conditions for strategic investments."
    recommendations = [
        "Consider increasing position sizes gradually",
        "Set stop-loss orders at 10% below current prices",
        "Diversify into emerging altcoins",
        "Monitor regulatory news for market impact"
    ]
    
    return schemas.AIResponse(
        response=response,
        analysis=analysis,
        recommendations=recommendations
        ) 