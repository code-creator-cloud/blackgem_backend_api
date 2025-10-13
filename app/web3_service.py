#!/usr/bin/env python3
"""
Web3 Service for USDT TRC20 and BEP20 Integration
"""

import os
import json
import asyncio
import secrets
import string
from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime, timedelta
import requests
from web3 import Web3
from tronpy import Tron
from tronpy.keys import PrivateKey

# Import models for database operations
from app import models
from app.database import SessionLocal

class Web3Service:
    def __init__(self):
        # Load environment variables
        self.tron_network = os.getenv("TRON_NETWORK", "mainnet")  # mainnet or testnet
        self.bsc_network = os.getenv("BSC_NETWORK", "mainnet")  # mainnet or testnet
        
        # Initialize Tron client
        if self.tron_network == "mainnet":
            self.tron = Tron(network='mainnet')
        else:
            self.tron = Tron(network='testnet')
        
        # Initialize Web3 for BSC
        if self.bsc_network == "mainnet":
            self.bsc_w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))
        else:
            self.bsc_w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545/'))
        
        # USDT Contract Addresses
        self.usdt_addresses = {
            "TRC20": {
                "mainnet": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # USDT on Tron mainnet
                "testnet": "TXYZopYRdj2D9XRtbG411XZZQkUBZ5K6b"   # USDT on Tron testnet
            },
            "BEP20": {
                "mainnet": "0x55d398326f99059fF775485246999027B3197955",  # USDT on BSC mainnet
                "testnet": "0x337610d27c682E347C9cD60BD4b3b107C9d34dDd"   # USDT on BSC testnet
            }
        }
        
        # Platform wallet addresses and private keys (you should store these securely)
        self.platform_wallets = {
            "TRC20": os.getenv("PLATFORM_TRC20_WALLET", "TYourPlatformWalletAddress"),
            "BEP20": os.getenv("PLATFORM_BEP20_WALLET", "0xYourPlatformWalletAddress")
        }
        
        # Platform private keys (for withdrawals) - STORE THESE SECURELY!
        self.platform_private_keys = {
            "TRC20": os.getenv("PLATFORM_TRC20_PRIVATE_KEY", ""),
            "BEP20": os.getenv("PLATFORM_BEP20_PRIVATE_KEY", "")
        }
        
        # USDT ABI (simplified for balance and transfer)
        self.usdt_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }
        ]

    def get_usdt_balance_trc20(self, wallet_address: str) -> float:
        """Get USDT balance on TRC20 network"""
        try:
            # Get USDT contract
            usdt_contract = self.tron.get_contract(self.usdt_addresses["TRC20"][self.tron_network])
            
            # Get balance (USDT has 6 decimals)
            balance = usdt_contract.functions.balanceOf(wallet_address) / 1_000_000
            
            return float(balance)
        except Exception as e:
            print(f"Error getting TRC20 USDT balance: {e}")
            return 0.0

    def get_usdt_balance_bep20(self, wallet_address: str) -> float:
        """Get USDT balance on BEP20 network"""
        try:
            # Get USDT contract
            usdt_contract = self.bsc_w3.eth.contract(
                address=self.usdt_addresses["BEP20"][self.bsc_network],
                abi=self.usdt_abi
            )
            
            # Get balance (USDT has 18 decimals on BSC)
            balance = usdt_contract.functions.balanceOf(wallet_address).call() / 1_000_000_000_000_000_000
            
            return float(balance)
        except Exception as e:
            print(f"Error getting BEP20 USDT balance: {e}")
            return 0.0

    def get_platform_balance_trc20(self) -> float:
        """Get platform USDT balance on TRC20"""
        return self.get_usdt_balance_trc20(self.platform_wallets["TRC20"])

    def get_platform_balance_bep20(self) -> float:
        """Get platform USDT balance on BEP20"""
        return self.get_usdt_balance_bep20(self.platform_wallets["BEP20"])

    def send_usdt_trc20(self, to_address: str, amount: float) -> Dict:
        """Send USDT on TRC20 network"""
        try:
            if not self.platform_private_keys["TRC20"]:
                return {"success": False, "error": "Platform private key not configured"}
            
            # Create private key object
            private_key = PrivateKey(bytes.fromhex(self.platform_private_keys["TRC20"]))
            
            # Get USDT contract
            usdt_contract = self.tron.get_contract(self.usdt_addresses["TRC20"][self.tron_network])
            
            # Convert amount to wei (USDT has 6 decimals)
            amount_wei = int(amount * 1_000_000)
            
            # Build transaction
            txn = usdt_contract.functions.transfer(to_address, amount_wei).with_owner(
                self.platform_wallets["TRC20"]
            ).fee_limit(100_000_000).build()
            
            # Sign and broadcast transaction
            signed_txn = txn.sign(private_key)
            tx_hash = signed_txn.broadcast().wait()
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount": amount,
                "to_address": to_address,
                "network": "TRC20"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_usdt_bep20(self, to_address: str, amount: float) -> Dict:
        """Send USDT on BEP20 network"""
        try:
            if not self.platform_private_keys["BEP20"]:
                return {"success": False, "error": "Platform private key not configured"}
            
            # Get USDT contract
            usdt_contract = self.bsc_w3.eth.contract(
                address=self.usdt_addresses["BEP20"][self.bsc_network],
                abi=self.usdt_abi
            )
            
            # Convert amount to wei (USDT has 18 decimals on BSC)
            amount_wei = int(amount * 1_000_000_000_000_000_000)
            
            # Get nonce
            nonce = self.bsc_w3.eth.get_transaction_count(self.platform_wallets["BEP20"])
            
            # Build transaction
            txn = usdt_contract.functions.transfer(to_address, amount_wei).build_transaction({
                'from': self.platform_wallets["BEP20"],
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': self.bsc_w3.eth.gas_price
            })
            
            # Sign transaction
            signed_txn = self.bsc_w3.eth.account.sign_transaction(
                txn, 
                self.platform_private_keys["BEP20"]
            )
            
            # Send transaction
            tx_hash = self.bsc_w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "amount": amount,
                "to_address": to_address,
                "network": "BEP20"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_transaction_trc20(self, tx_hash: str, expected_amount: float, to_address: str) -> Dict:
        """Verify TRC20 transaction"""
        try:
            # Get transaction info
            tx_info = self.tron.get_transaction(tx_hash)
            
            if not tx_info:
                return {"verified": False, "error": "Transaction not found"}
            
            # Check if transaction is confirmed
            if tx_info.get('ret', [{}])[0].get('contractRet') != 'SUCCESS':
                return {"verified": False, "error": "Transaction failed"}
            
            # Get contract info
            contract_info = tx_info.get('raw_data', {}).get('contract', [{}])[0]
            
            # Check if it's a USDT transfer
            if contract_info.get('type') != 'TriggerSmartContract':
                return {"verified": False, "error": "Not a smart contract transaction"}
            
            # Get transfer details
            parameter = contract_info.get('parameter', {})
            value = parameter.get('value', {})
            
            # Check recipient address
            if value.get('to_address') != self.usdt_addresses["TRC20"][self.tron_network]:
                return {"verified": False, "error": "Not a USDT transaction"}
            
            # Check amount (USDT has 6 decimals)
            amount = int(value.get('data', '')[72:136], 16) / 1_000_000
            
            # Check if amount matches expected
            if abs(amount - expected_amount) > 0.01:  # Allow small difference for fees
                return {"verified": False, "error": f"Amount mismatch: expected {expected_amount}, got {amount}"}
            
            return {
                "verified": True,
                "amount": amount,
                "from_address": self.tron.address.from_hex(value.get('owner_address')),
                "to_address": to_address,
                "tx_hash": tx_hash,
                "network": "TRC20"
            }
            
        except Exception as e:
            return {"verified": False, "error": str(e)}

    def verify_transaction_bep20(self, tx_hash: str, expected_amount: float, to_address: str) -> Dict:
        """Verify BEP20 transaction"""
        try:
            # Get transaction receipt
            tx_receipt = self.bsc_w3.eth.get_transaction_receipt(tx_hash)
            
            if not tx_receipt or tx_receipt['status'] != 1:
                return {"verified": False, "error": "Transaction failed or not found"}
            
            # Get transaction
            tx = self.bsc_w3.eth.get_transaction(tx_hash)
            
            # Check if it's a USDT transfer
            if tx['to'].lower() != self.usdt_addresses["BEP20"][self.bsc_network].lower():
                return {"verified": False, "error": "Not a USDT transaction"}
            
            # Parse transfer data
            usdt_contract = self.bsc_w3.eth.contract(
                address=self.usdt_addresses["BEP20"][self.bsc_network],
                abi=self.usdt_abi
            )
            
            # Decode function call
            func_obj, func_params = usdt_contract.decode_function_result('transfer', tx['input'])
            
            # Check amount (USDT has 18 decimals on BSC)
            amount = func_params[1] / 1_000_000_000_000_000_000
            
            # Check if amount matches expected
            if abs(amount - expected_amount) > 0.01:  # Allow small difference for fees
                return {"verified": False, "error": f"Amount mismatch: expected {expected_amount}, got {amount}"}
            
            return {
                "verified": True,
                "amount": amount,
                "from_address": tx['from'],
                "to_address": to_address,
                "tx_hash": tx_hash,
                "network": "BEP20"
            }
            
        except Exception as e:
            return {"verified": False, "error": str(e)}

    def get_deposit_address(self, network: str) -> str:
        """Get deposit address for specified network"""
        if network.upper() == "TRC20":
            return self.platform_wallets["TRC20"]
        elif network.upper() == "BEP20":
            return self.platform_wallets["BEP20"]
        else:
            raise ValueError(f"Unsupported network: {network}")

    def convert_usdt_to_usd(self, usdt_amount: float) -> float:
        """Convert USDT amount to USD (1:1 for USDT)"""
        return usdt_amount  # USDT is pegged to USD

    def convert_usd_to_usdt(self, usd_amount: float) -> float:
        """Convert USD amount to USDT (1:1 for USDT)"""
        return usd_amount  # USD to USDT is 1:1

    def generate_deposit_address(self, network: str) -> str:
        """Generate a unique deposit address for the specified network"""
        if network.upper() == "TRC20":
            # Generate a Tron address (base58 format)
            # For demo purposes, we'll generate a random address
            # In production, you'd use proper key generation
            chars = string.ascii_letters + string.digits
            address = "T" + ''.join(secrets.choice(chars) for _ in range(33))
            return address
        elif network.upper() == "BEP20":
            # Generate a BSC address (hex format)
            # For demo purposes, we'll generate a random address
            # In production, you'd use proper key generation
            chars = string.hexdigits.lower()
            address = "0x" + ''.join(secrets.choice(chars) for _ in range(40))
            return address
        else:
            raise ValueError(f"Unsupported network: {network}")

    def create_deposit_address(self, user_id: int, amount: float, network: str) -> Dict:
        """Create a new deposit address for a user"""
        db = SessionLocal()
        try:
            # Generate unique address
            address = self.generate_deposit_address(network)
            
            # Set expiration to 24 hours from now
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Create deposit address record
            deposit_address = models.Web3DepositAddress(
                user_id=user_id,
                address=address,
                network=network.upper(),
                amount=amount,
                status="pending",
                expires_at=expires_at
            )
            
            db.add(deposit_address)
            db.commit()
            db.refresh(deposit_address)
            
            return {
                "id": deposit_address.id,
                "user_id": deposit_address.user_id,
                "amount": deposit_address.amount,
                "network": deposit_address.network,
                "address": deposit_address.address,
                "expires_at": deposit_address.expires_at,
                "status": deposit_address.status,
                "created_at": deposit_address.created_at
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_deposit_address_status(self, address_id: int) -> Dict:
        """Get the status of a deposit address"""
        db = SessionLocal()
        try:
            deposit_address = db.query(models.Web3DepositAddress).filter(
                models.Web3DepositAddress.id == address_id
            ).first()
            
            if not deposit_address:
                raise ValueError("Deposit address not found")
            
            return {
                "id": deposit_address.id,
                "status": deposit_address.status,
                "amount": deposit_address.amount,
                "network": deposit_address.network,
                "address": deposit_address.address,
                "expires_at": deposit_address.expires_at,
                "created_at": deposit_address.created_at
            }
        finally:
            db.close()

    def expire_deposit_addresses(self):
        """Expire deposit addresses that are older than 24 hours"""
        db = SessionLocal()
        try:
            expired_addresses = db.query(models.Web3DepositAddress).filter(
                models.Web3DepositAddress.status == "pending",
                models.Web3DepositAddress.expires_at < datetime.utcnow()
            ).all()
            
            for address in expired_addresses:
                address.status = "expired"
            
            db.commit()
            return len(expired_addresses)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_network_info(self, network: str) -> Dict:
        """Get network information"""
        network_info = {
            "TRC20": {
                "name": "Tron Network",
                "currency": "USDT",
                "decimals": 6,
                "explorer": "https://tronscan.org",
                "deposit_address": self.platform_wallets["TRC20"],
                "min_deposit": 10.0,
                "max_deposit": 100000.0,
                "min_withdrawal": 10.0,
                "max_withdrawal": 100000.0,
                "withdrawal_fee": 1.0  # USDT fee for TRC20
            },
            "BEP20": {
                "name": "Binance Smart Chain",
                "currency": "USDT",
                "decimals": 18,
                "explorer": "https://bscscan.com",
                "deposit_address": self.platform_wallets["BEP20"],
                "min_deposit": 10.0,
                "max_deposit": 100000.0,
                "min_withdrawal": 10.0,
                "max_withdrawal": 100000.0,
                "withdrawal_fee": 0.5  # USDT fee for BEP20
            }
        }
        
        return network_info.get(network.upper(), {})

    def check_withdrawal_eligibility(self, network: str, amount: float, user_balance: float) -> Dict:
        """Check if user can withdraw the specified amount"""
        network_info = self.get_network_info(network)
        
        if not network_info:
            return {"eligible": False, "error": "Invalid network"}
        
        # Check minimum withdrawal
        if amount < network_info.get("min_withdrawal", 10.0):
            return {
                "eligible": False, 
                "error": f"Amount too low. Minimum withdrawal is {network_info['min_withdrawal']} USDT"
            }
        
        # Check maximum withdrawal
        if amount > network_info.get("max_withdrawal", 100000.0):
            return {
                "eligible": False, 
                "error": f"Amount too high. Maximum withdrawal is {network_info['max_withdrawal']} USDT"
            }
        
        # Check user balance
        if amount > user_balance:
            return {
                "eligible": False, 
                "error": f"Insufficient balance. You have ${user_balance} USD, trying to withdraw ${amount} USD"
            }
        
        # Check platform balance
        platform_balance = 0
        if network.upper() == "TRC20":
            platform_balance = self.get_platform_balance_trc20()
        elif network.upper() == "BEP20":
            platform_balance = self.get_platform_balance_bep20()
        
        if amount > platform_balance:
            return {
                "eligible": False, 
                "error": f"Insufficient platform balance. Platform has {platform_balance} USDT, trying to withdraw {amount} USDT"
            }
        
        return {"eligible": True, "platform_balance": platform_balance}

    async def monitor_deposits(self, db_session, check_interval: int = 30):
        """Monitor for new deposits (background task)"""
        while True:
            try:
                # First, expire old deposit addresses
                self.expire_deposit_addresses()
                
                # Get pending deposit addresses
                pending_addresses = db_session.query(models.Web3DepositAddress).filter(
                    models.Web3DepositAddress.status == "pending",
                    models.Web3DepositAddress.expires_at > datetime.utcnow()
                ).all()
                
                for deposit_address in pending_addresses:
                    # Check if funds were received at the address
                    if deposit_address.network == "TRC20":
                        balance = self.get_usdt_balance_trc20(deposit_address.address)
                    elif deposit_address.network == "BEP20":
                        balance = self.get_usdt_balance_bep20(deposit_address.address)
                    else:
                        continue
                    
                    # If funds were received and amount matches
                    if balance >= deposit_address.amount:
                        # Mark deposit address as completed
                        deposit_address.status = "completed"
                        deposit_address.completed_at = datetime.utcnow()
                        
                        # Create transaction record
                        transaction = models.Transaction(
                            user_id=deposit_address.user_id,
                            type="deposit",
                            amount=deposit_address.amount,
                            currency="USDT",
                            status="completed",
                            provider=deposit_address.network,
                            network=deposit_address.network,
                            deposit_address_id=deposit_address.id,
                            description=f"USDT deposit on {deposit_address.network} network",
                            notes="Auto-verified from deposit address"
                        )
                        
                        # Update user balance
                        user = db_session.query(models.User).filter(
                            models.User.id == deposit_address.user_id
                        ).first()
                        
                        if user:
                            usd_amount = self.convert_usdt_to_usd(deposit_address.amount)
                            user.balance += usd_amount
                        
                        db_session.add(transaction)
                        db_session.commit()
                        
                        print(f"✅ Auto-verified deposit: {deposit_address.amount} USDT -> {usd_amount} USD")
                    else:
                        print(f"⏳ Waiting for deposit: {deposit_address.amount} USDT at {deposit_address.address}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Error monitoring deposits: {e}")
                await asyncio.sleep(check_interval)

# Create global instance
web3_service = Web3Service() 