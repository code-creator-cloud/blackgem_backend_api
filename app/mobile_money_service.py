import httpx
import json
import hashlib
import hmac
import time
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
import sys
import os

# Add the parent directory to the path to import the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mobile_money_config import MobileMoneyConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileMoneyService:
    def __init__(self):
        # Load configuration
        self.config = MobileMoneyConfig()
        
        # MTN Mobile Money API Configuration
        mtn_config = self.config.get_mtn_config()
        self.mtn_api_key = mtn_config["api_key"]
        self.mtn_api_secret = mtn_config["api_secret"]
        self.mtn_base_url = mtn_config["base_url"]
        self.mtn_merchant_id = mtn_config["merchant_id"]
        self.mtn_callback_url = mtn_config["callback_url"]
        
        # Orange Money API Configuration
        orange_config = self.config.get_orange_config()
        self.orange_api_key = orange_config["api_key"]
        self.orange_api_secret = orange_config["api_secret"]
        self.orange_base_url = orange_config["base_url"]
        self.orange_merchant_id = orange_config["merchant_id"]
        self.orange_callback_url = orange_config["callback_url"]
        
        # Transaction status tracking
        self.pending_transactions = {}
    
    def _generate_mtn_signature(self, data: str, timestamp: str) -> str:
        """Generate MTN API signature for authentication"""
        message = f"{data}{timestamp}{self.mtn_api_secret}"
        signature = hmac.new(
            self.mtn_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _generate_orange_signature(self, data: str, timestamp: str) -> str:
        """Generate Orange Money API signature for authentication"""
        message = f"{data}{timestamp}{self.orange_api_secret}"
        signature = hmac.new(
            self.orange_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def initiate_mtn_deposit(self, phone_number: str, amount: float, user_id: int) -> Dict:
        """Initiate MTN Mobile Money deposit"""
        try:
            timestamp = str(int(time.time()))
            transaction_id = f"MTN_DEP_{timestamp}_{user_id}"
            
            payload = {
                "merchant_id": self.mtn_merchant_id,
                "amount": amount,
                "currency": "XAF",
                "phone_number": phone_number,
                "transaction_id": transaction_id,
                "description": f"Deposit to BlackGerm account",
                "callback_url": "https://your-domain.com/api/mobile-money/mtn/callback"
            }
            
            data_string = json.dumps(payload, sort_keys=True)
            signature = self._generate_mtn_signature(data_string, timestamp)
            
            headers = {
                "Authorization": f"Bearer {self.mtn_api_key}",
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mtn_base_url}/collections",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.pending_transactions[transaction_id] = {
                        "provider": "MTN",
                        "type": "deposit",
                        "amount": amount,
                        "phone_number": phone_number,
                        "user_id": user_id,
                        "status": "pending",
                        "created_at": datetime.utcnow()
                    }
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": "pending",
                        "message": "MTN Mobile Money deposit initiated successfully",
                        "provider": "MTN",
                        "amount": amount,
                        "phone_number": phone_number
                    }
                else:
                    logger.error(f"MTN API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"MTN API error: {response.status_code}",
                        "message": "Failed to initiate MTN deposit"
                    }
                    
        except Exception as e:
            logger.error(f"MTN deposit error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate MTN deposit"
            }
    
    async def initiate_orange_deposit(self, phone_number: str, amount: float, user_id: int) -> Dict:
        """Initiate Orange Money deposit"""
        try:
            timestamp = str(int(time.time()))
            transaction_id = f"ORANGE_DEP_{timestamp}_{user_id}"
            
            payload = {
                "merchant_id": self.orange_merchant_id,
                "amount": amount,
                "currency": "XAF",
                "phone_number": phone_number,
                "transaction_id": transaction_id,
                "description": f"Deposit to BlackGerm account",
                "callback_url": "https://your-domain.com/api/mobile-money/orange/callback"
            }
            
            data_string = json.dumps(payload, sort_keys=True)
            signature = self._generate_orange_signature(data_string, timestamp)
            
            headers = {
                "Authorization": f"Bearer {self.orange_api_key}",
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orange_base_url}/collections",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.pending_transactions[transaction_id] = {
                        "provider": "Orange",
                        "type": "deposit",
                        "amount": amount,
                        "phone_number": phone_number,
                        "user_id": user_id,
                        "status": "pending",
                        "created_at": datetime.utcnow()
                    }
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": "pending",
                        "message": "Orange Money deposit initiated successfully",
                        "provider": "Orange",
                        "amount": amount,
                        "phone_number": phone_number
                    }
                else:
                    logger.error(f"Orange API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Orange API error: {response.status_code}",
                        "message": "Failed to initiate Orange deposit"
                    }
                    
        except Exception as e:
            logger.error(f"Orange deposit error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate Orange deposit"
            }
    
    async def initiate_mtn_withdrawal(self, phone_number: str, amount: float, user_id: int) -> Dict:
        """Initiate MTN Mobile Money withdrawal"""
        try:
            timestamp = str(int(time.time()))
            transaction_id = f"MTN_WIT_{timestamp}_{user_id}"
            
            payload = {
                "merchant_id": self.mtn_merchant_id,
                "amount": amount,
                "currency": "XAF",
                "phone_number": phone_number,
                "transaction_id": transaction_id,
                "description": f"Withdrawal from BlackGerm account",
                "callback_url": "https://your-domain.com/api/mobile-money/mtn/withdrawal-callback"
            }
            
            data_string = json.dumps(payload, sort_keys=True)
            signature = self._generate_mtn_signature(data_string, timestamp)
            
            headers = {
                "Authorization": f"Bearer {self.mtn_api_key}",
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mtn_base_url}/disbursements",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.pending_transactions[transaction_id] = {
                        "provider": "MTN",
                        "type": "withdrawal",
                        "amount": amount,
                        "phone_number": phone_number,
                        "user_id": user_id,
                        "status": "pending",
                        "created_at": datetime.utcnow()
                    }
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": "pending",
                        "message": "MTN Mobile Money withdrawal initiated successfully",
                        "provider": "MTN",
                        "amount": amount,
                        "phone_number": phone_number
                    }
                else:
                    logger.error(f"MTN withdrawal API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"MTN API error: {response.status_code}",
                        "message": "Failed to initiate MTN withdrawal"
                    }
                    
        except Exception as e:
            logger.error(f"MTN withdrawal error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate MTN withdrawal"
            }
    
    async def initiate_orange_withdrawal(self, phone_number: str, amount: float, user_id: int) -> Dict:
        """Initiate Orange Money withdrawal"""
        try:
            timestamp = str(int(time.time()))
            transaction_id = f"ORANGE_WIT_{timestamp}_{user_id}"
            
            payload = {
                "merchant_id": self.orange_merchant_id,
                "amount": amount,
                "currency": "XAF",
                "phone_number": phone_number,
                "transaction_id": transaction_id,
                "description": f"Withdrawal from BlackGerm account",
                "callback_url": "https://your-domain.com/api/mobile-money/orange/withdrawal-callback"
            }
            
            data_string = json.dumps(payload, sort_keys=True)
            signature = self._generate_orange_signature(data_string, timestamp)
            
            headers = {
                "Authorization": f"Bearer {self.orange_api_key}",
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orange_base_url}/disbursements",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.pending_transactions[transaction_id] = {
                        "provider": "Orange",
                        "type": "withdrawal",
                        "amount": amount,
                        "phone_number": phone_number,
                        "user_id": user_id,
                        "status": "pending",
                        "created_at": datetime.utcnow()
                    }
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": "pending",
                        "message": "Orange Money withdrawal initiated successfully",
                        "provider": "Orange",
                        "amount": amount,
                        "phone_number": phone_number
                    }
                else:
                    logger.error(f"Orange withdrawal API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Orange API error: {response.status_code}",
                        "message": "Failed to initiate Orange withdrawal"
                    }
                    
        except Exception as e:
            logger.error(f"Orange withdrawal error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate Orange withdrawal"
            }
    
    async def check_transaction_status(self, transaction_id: str) -> Dict:
        """Check the status of a mobile money transaction"""
        if transaction_id in self.pending_transactions:
            transaction = self.pending_transactions[transaction_id]
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": transaction["status"],
                "provider": transaction["provider"],
                "type": transaction["type"],
                "amount": transaction["amount"],
                "phone_number": transaction["phone_number"],
                "created_at": transaction["created_at"].isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Transaction not found",
                "message": "Transaction ID not found in pending transactions"
            }
    
    async def process_callback(self, provider: str, callback_data: Dict) -> Dict:
        """Process callback from mobile money providers"""
        try:
            transaction_id = callback_data.get("transaction_id")
            status = callback_data.get("status")
            
            if transaction_id in self.pending_transactions:
                self.pending_transactions[transaction_id]["status"] = status
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "status": status,
                    "provider": provider,
                    "message": f"{provider} transaction status updated"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction not found",
                    "message": "Transaction ID not found in pending transactions"
                }
                
        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process callback"
            }
    
    def validate_phone_number(self, phone_number: str, provider: str) -> bool:
        """Validate phone number format for MTN or Orange"""
        return self.config.validate_phone_number(phone_number, provider)
    
    def validate_amount(self, amount: float, transaction_type: str) -> bool:
        """Validate transaction amount"""
        return self.config.validate_amount(amount, transaction_type)
    
    def calculate_fee(self, amount: float, provider: str, transaction_type: str) -> float:
        """Calculate transaction fee"""
        return self.config.calculate_fee(amount, provider, transaction_type)

# Create a global instance
mobile_money_service = MobileMoneyService() 