from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv
from app.database import engine, get_db
from app import models, schemas, auth
from app.routers import users, transactions, ai_assistant
from app.routers import crypto
from app.routers import payments
from app.routers import notifications
from app.routers import mobile_money
from app.routers import admin
from app.routers import web3_deposits
from app.background_tasks import start_background_tasks
from app.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Black Germ",
    description="A secure cryptocurrency investment platform with AI-powered insights",
    version="1.0.0"
)
logger.info("Black Germ FastAPI application initialized")

# Add CORS middleware
import os
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["ai"])
app.include_router(crypto.router, prefix="/api/crypto", tags=["crypto"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(mobile_money.router, prefix="/api/mobile-money", tags=["mobile-money"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(web3_deposits.router, prefix="/api/web3", tags=["web3"])
logger.info("API routers included")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    try:
        return {"message": "Welcome to Black Germ"}
    except Exception as e:
        logger.error(f"Root endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Server error",
                "message": "An error occurred while processing the request."
            }
        )

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    try:
        return {"status": "healthy", "message": "Black Germ API is running"}
    except Exception as e:
        logger.error(f"Health check endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Server error",
                "message": "An error occurred while checking server health."
            }
        )

@app.get("/api/dashboard", response_model=schemas.DashboardData)
async def get_dashboard(
    current_user: models.User = Depends(auth.get_current_active_user), 
    db: Session = Depends(get_db)
):
    """Get user dashboard data"""
    logger.info(f"Fetching dashboard data for user {current_user.email}")
    try:
        # Get user's transactions
        transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()
        
        # Calculate totals
        total_deposits = sum(t.amount for t in transactions if t.type == "deposit" and t.status == "completed")
        total_withdrawals = sum(t.amount for t in transactions if t.type == "withdraw" and t.status == "completed")
        current_balance = current_user.balance
        
        logger.info(f"Dashboard data retrieved for {current_user.email}: {len(transactions)} transactions")
        return schemas.DashboardData(
            user=current_user,
            transactions=transactions,
            total_deposits=total_deposits,
            total_withdrawals=total_withdrawals,
            current_balance=current_balance
        )
    except Exception as e:
        logger.error(f"Failed to fetch dashboard data for {current_user.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch dashboard data",
                "message": "An error occurred while fetching dashboard data."
            }
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting background tasks")
    start_background_tasks()
    logger.info("Starting Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8000)