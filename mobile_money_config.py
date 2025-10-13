"""
Mobile Money Configuration
Configuration settings for MTN and Orange Cameroon mobile money integration
"""

import os
from typing import Dict, Any

class MobileMoneyConfig:
    """Configuration class for mobile money services"""
    
    # MTN Mobile Money Configuration
    MTN_API_KEY = os.getenv("MTN_API_KEY", "your_mtn_api_key")
    MTN_API_SECRET = os.getenv("MTN_API_SECRET", "your_mtn_api_secret")
    MTN_BASE_URL = os.getenv("MTN_BASE_URL", "https://api.mtn.com/v1")
    MTN_MERCHANT_ID = os.getenv("MTN_MERCHANT_ID", "your_mtn_merchant_id")
    
    # Orange Money Configuration
    ORANGE_API_KEY = os.getenv("ORANGE_API_KEY", "your_orange_api_key")
    ORANGE_API_SECRET = os.getenv("ORANGE_API_SECRET", "your_orange_api_secret")
    ORANGE_BASE_URL = os.getenv("ORANGE_BASE_URL", "https://api.orange.com/v1")
    ORANGE_MERCHANT_ID = os.getenv("ORANGE_MERCHANT_ID", "your_orange_merchant_id")
    
    # Transaction Limits
    MIN_DEPOSIT_AMOUNT = 100.0  # 100 XAF
    MAX_DEPOSIT_AMOUNT = 500000.0  # 500,000 XAF
    MIN_WITHDRAWAL_AMOUNT = 100.0  # 100 XAF
    MAX_WITHDRAWAL_AMOUNT = 500000.0  # 500,000 XAF
    
    # Transaction Fees (in XAF)
    MTN_DEPOSIT_FEE = 0.0  # No fee for deposits
    MTN_WITHDRAWAL_FEE = 50.0  # 50 XAF withdrawal fee
    ORANGE_DEPOSIT_FEE = 0.0  # No fee for deposits
    ORANGE_WITHDRAWAL_FEE = 50.0  # 50 XAF withdrawal fee
    
    # Phone Number Validation
    CAMEROON_COUNTRY_CODE = "237"
    MTN_PREFIXES = ["6", "7"]  # MTN Cameroon prefixes
    ORANGE_PREFIXES = ["6", "7"]  # Orange Cameroon prefixes
    
    # Callback URLs
    MTN_CALLBACK_URL = os.getenv("MTN_CALLBACK_URL", "https://your-domain.com/api/mobile-money/mtn/callback")
    ORANGE_CALLBACK_URL = os.getenv("ORANGE_CALLBACK_URL", "https://your-domain.com/api/mobile-money/orange/callback")
    
    # Transaction Timeout (in seconds)
    TRANSACTION_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def get_mtn_config(cls) -> Dict[str, Any]:
        """Get MTN configuration"""
        return {
            "api_key": cls.MTN_API_KEY,
            "api_secret": cls.MTN_API_SECRET,
            "base_url": cls.MTN_BASE_URL,
            "merchant_id": cls.MTN_MERCHANT_ID,
            "callback_url": cls.MTN_CALLBACK_URL,
            "deposit_fee": cls.MTN_DEPOSIT_FEE,
            "withdrawal_fee": cls.MTN_WITHDRAWAL_FEE
        }
    
    @classmethod
    def get_orange_config(cls) -> Dict[str, Any]:
        """Get Orange configuration"""
        return {
            "api_key": cls.ORANGE_API_KEY,
            "api_secret": cls.ORANGE_API_SECRET,
            "base_url": cls.ORANGE_BASE_URL,
            "merchant_id": cls.ORANGE_MERCHANT_ID,
            "callback_url": cls.ORANGE_CALLBACK_URL,
            "deposit_fee": cls.ORANGE_DEPOSIT_FEE,
            "withdrawal_fee": cls.ORANGE_WITHDRAWAL_FEE
        }
    
    @classmethod
    def validate_amount(cls, amount: float, transaction_type: str) -> bool:
        """Validate transaction amount"""
        if transaction_type == "deposit":
            return cls.MIN_DEPOSIT_AMOUNT <= amount <= cls.MAX_DEPOSIT_AMOUNT
        elif transaction_type == "withdrawal":
            return cls.MIN_WITHDRAWAL_AMOUNT <= amount <= cls.MAX_WITHDRAWAL_AMOUNT
        return False
    
    @classmethod
    def calculate_fee(cls, amount: float, provider: str, transaction_type: str) -> float:
        """Calculate transaction fee"""
        if provider.upper() == "MTN":
            if transaction_type == "deposit":
                return cls.MTN_DEPOSIT_FEE
            elif transaction_type == "withdrawal":
                return cls.MTN_WITHDRAWAL_FEE
        elif provider.upper() == "ORANGE":
            if transaction_type == "deposit":
                return cls.ORANGE_DEPOSIT_FEE
            elif transaction_type == "withdrawal":
                return cls.ORANGE_WITHDRAWAL_FEE
        return 0.0
    
    @classmethod
    def validate_phone_number(cls, phone_number: str, provider: str) -> bool:
        """Validate phone number format for Cameroon mobile money"""
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Check if it's a valid Cameroon number
        if len(clean_number) == 9 and clean_number.startswith(tuple(cls.MTN_PREFIXES + cls.ORANGE_PREFIXES)):
            return True
        elif len(clean_number) == 12 and clean_number.startswith(cls.CAMEROON_COUNTRY_CODE):
            # Remove country code and check
            local_number = clean_number[3:]
            return local_number.startswith(tuple(cls.MTN_PREFIXES + cls.ORANGE_PREFIXES))
        
        return False

# Environment variables template
ENV_TEMPLATE = """
# Mobile Money Configuration
# MTN Mobile Money
MTN_API_KEY=your_mtn_api_key_here
MTN_API_SECRET=your_mtn_api_secret_here
MTN_BASE_URL=https://api.mtn.com/v1
MTN_MERCHANT_ID=your_mtn_merchant_id_here

# Orange Money
ORANGE_API_KEY=your_orange_api_key_here
ORANGE_API_SECRET=your_orange_api_secret_here
ORANGE_BASE_URL=https://api.orange.com/v1
ORANGE_MERCHANT_ID=your_orange_merchant_id_here

# Callback URLs (update with your domain)
MTN_CALLBACK_URL=https://your-domain.com/api/mobile-money/mtn/callback
ORANGE_CALLBACK_URL=https://your-domain.com/api/mobile-money/orange/callback
"""

if __name__ == "__main__":
    print("Mobile Money Configuration")
    print("=" * 30)
    print(f"Min Deposit Amount: {MobileMoneyConfig.MIN_DEPOSIT_AMOUNT} XAF")
    print(f"Max Deposit Amount: {MobileMoneyConfig.MAX_DEPOSIT_AMOUNT} XAF")
    print(f"Min Withdrawal Amount: {MobileMoneyConfig.MIN_WITHDRAWAL_AMOUNT} XAF")
    print(f"Max Withdrawal Amount: {MobileMoneyConfig.MAX_WITHDRAWAL_AMOUNT} XAF")
    print(f"MTN Withdrawal Fee: {MobileMoneyConfig.MTN_WITHDRAWAL_FEE} XAF")
    print(f"Orange Withdrawal Fee: {MobileMoneyConfig.ORANGE_WITHDRAWAL_FEE} XAF")
    print("\nEnvironment Variables Template:")
    print(ENV_TEMPLATE) 