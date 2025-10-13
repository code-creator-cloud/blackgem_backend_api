import stripe 
import json
from typing import Dict, Optional
from datetime import datetime
import os

# Initialize Stripe (you'll need to set your API keys)
stripe.api_key = "sk_test_your_stripe_test_key_here"  # Replace with your actual test key

class PaymentService:
    def __init__(self):
        self.currency = "usd"
    
    def create_payment_intent(self, amount: float, user_email: str) -> Optional[Dict]:
        """Create a payment intent for deposit"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=self.currency,
                metadata={
                    "user_email": user_email,
                    "type": "deposit"
                }
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": self.currency
            }
        except Exception as e:
            print(f"Error creating payment intent: {e}")
            return None
    
    def confirm_payment(self, payment_intent_id: str) -> Optional[Dict]:
        """Confirm a payment and return status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "status": intent.status,
                "amount": intent.amount / 100,  # Convert from cents
                "currency": intent.currency,
                "created": datetime.fromtimestamp(intent.created)
            }
        except Exception as e:
            print(f"Error confirming payment: {e}")
            return None
    
    def create_withdrawal_request(self, amount: float, wallet_address: str, user_email: str) -> Optional[Dict]:
        """Create a withdrawal request"""
        try:
            # In a real implementation, you'd integrate with a crypto payment processor
            # For now, we'll simulate the withdrawal process
            withdrawal_id = f"withdrawal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "withdrawal_id": withdrawal_id,
                "amount": amount,
                "wallet_address": wallet_address,
                "status": "pending",
                "estimated_completion": datetime.utcnow().isoformat(),
                "network_fee": 0.001  # Simulated network fee
            }
        except Exception as e:
            print(f"Error creating withdrawal request: {e}")
            return None
    
    def get_payment_methods(self) -> Dict:
        """Get available payment methods"""
        return {
            "credit_card": {
                "enabled": True,
                "min_amount": 10.0,
                "max_amount": 10000.0,
                "processing_fee": 0.029  # 2.9%
            },
            "bank_transfer": {
                "enabled": True,
                "min_amount": 50.0,
                "max_amount": 50000.0,
                "processing_fee": 0.0
            },
            "crypto": {
                "enabled": True,
                "min_amount": 5.0,
                "max_amount": 100000.0,
                "processing_fee": 0.005  # 0.5%
            }
        }

# Create a global instance
payment_service = PaymentService()