import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import time

class CryptoService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.supported_coins = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana"]
    
    def get_crypto_price(self, coin_id: str) -> Optional[float]:
        """Get current price of a cryptocurrency"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd"
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get("usd")
            return None
        except Exception as e:
            print(f"Error fetching price for {coin_id}: {e}")
            return None
    
    def get_crypto_prices(self) -> Dict[str, float]:
        """Get prices for all supported cryptocurrencies"""
        prices = {}
        for coin in self.supported_coins:
            price = self.get_crypto_price(coin)
            if price:
                prices[coin] = price
        return prices
    
    def get_crypto_market_data(self, coin_id: str) -> Optional[Dict]:
        """Get detailed market data for a cryptocurrency"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "symbol": data.get("symbol").upper(),
                    "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "volume_24h": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                    "price_change_24h": data.get("market_data", {}).get("price_change_24h"),
                    "price_change_percentage_24h": data.get("market_data", {}).get("price_change_percentage_24h")
                }
            return None
        except Exception as e:
            print(f"Error fetching market data for {coin_id}: {e}")
            return None
    
    def calculate_investment_value(self, coin_id: str, amount: float) -> Optional[Dict]:
        """Calculate investment value and potential returns"""
        price = self.get_crypto_price(coin_id)
        if price:
            coins_purchased = amount / price
            return {
                "coin_id": coin_id,
                "investment_amount": amount,
                "current_price": price,
                "coins_purchased": coins_purchased,
                "current_value": coins_purchased * price,
                "potential_profit": (coins_purchased * price) - amount
            }
        return None

# Create a global instance
crypto_service = CryptoService()