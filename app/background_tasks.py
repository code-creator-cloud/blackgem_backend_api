#!/usr/bin/env python3
"""
Background tasks for Web3 deposit monitoring
"""

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.web3_service import web3_service
from app import models

async def monitor_web3_deposits():
    """Background task to monitor Web3 deposits"""
    while True:
        try:
            db = SessionLocal()
            # Use the new monitoring system from web3_service
            await web3_service.monitor_deposits(db)
            db.close()
        except Exception as e:
            print(f"Error in deposit monitoring: {e}")
            await asyncio.sleep(30)

def start_background_tasks():
    """Start background tasks"""
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_web3_deposits())
    print("🚀 Background tasks started") 