import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CryptoService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.prices_cache = {}
        self.last_update = None
        self.supported_coins = [
            {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'},
            {'id': 'ethereum', 'symbol': 'eth', 'name': 'Ethereum'},
            {'id': 'binancecoin', 'symbol': 'bnb', 'name': 'BNB'},
            {'id': 'cardano', 'symbol': 'ada', 'name': 'Cardano'},
            {'id': 'solana', 'symbol': 'sol', 'name': 'Solana'},
            {'id': 'ripple', 'symbol': 'xrp', 'name': 'XRP'},
            {'id': 'polkadot', 'symbol': 'dot', 'name': 'Polkadot'},
            {'id': 'dogecoin', 'symbol': 'doge', 'name': 'Dogecoin'},
            {'id': 'avalanche-2', 'symbol': 'avax', 'name': 'Avalanche'},
            {'id': 'chainlink', 'symbol': 'link', 'name': 'Chainlink'}
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'CharlyNet-Crypto-API/1.0'
        })

    def _make_request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make HTTP request to CoinGecko API with error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:  # Rate limit
                logging.warning("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return None
        except ValueError as e:
            logging.error(f"Invalid JSON response: {str(e)}")
            return None

    def update_prices(self):
        """Fetch and update current prices for all supported cryptocurrencies"""
        try:
            coin_ids = ','.join([coin['id'] for coin in self.supported_coins])
            params = {
                'ids': coin_ids,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            data = self._make_request('simple/price', params)
            if not data:
                logging.error("Failed to fetch price data")
                return False
            
            # Update cache with new data
            for coin in self.supported_coins:
                coin_id = coin['id']
                if coin_id in data:
                    coin_data = data[coin_id]
                    self.prices_cache[coin['symbol']] = {
                        'id': coin_id,
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'current_price': coin_data.get('usd', 0),
                        'price_change_24h': coin_data.get('usd_24h_change', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'volume_24h': coin_data.get('usd_24h_vol', 0)
                    }
            
            self.last_update = datetime.now().isoformat()
            logging.info(f"Updated prices for {len(self.prices_cache)} cryptocurrencies")
            return True
            
        except Exception as e:
            logging.error(f"Error updating prices: {str(e)}")
            return False

    def get_all_prices(self) -> Dict:
        """Get current prices for all cryptocurrencies"""
        return self.prices_cache

    def get_price_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get current price for a specific cryptocurrency by symbol"""
        return self.prices_cache.get(symbol.lower())

    def get_price_history(self, symbol: str, days: int = 7) -> Optional[List[Dict]]:
        """Get price history for a cryptocurrency"""
        try:
            # Find coin ID by symbol
            coin_id = None
            for coin in self.supported_coins:
                if coin['symbol'].lower() == symbol.lower():
                    coin_id = coin['id']
                    break
            
            if not coin_id:
                return None
            
            params = {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            endpoint = f"coins/{coin_id}/market_chart"
            data = self._make_request(endpoint, params)
            
            if not data or 'prices' not in data:
                return None
            
            # Format price history
            history = []
            for price_point in data['prices']:
                timestamp = price_point[0]
                price = price_point[1]
                history.append({
                    'timestamp': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                    'price': price
                })
            
            return history
            
        except Exception as e:
            logging.error(f"Error fetching history for {symbol}: {str(e)}")
            return None

    def get_supported_cryptocurrencies(self) -> List[Dict]:
        """Get list of supported cryptocurrencies"""
        return self.supported_coins

    def get_last_update_time(self) -> Optional[str]:
        """Get timestamp of last price update"""
        return self.last_update
