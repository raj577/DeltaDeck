# Angel One API integration module
import os
import asyncio
from typing import Optional, Dict, Any, List
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
from logzero import logger
from pydantic import BaseModel
import json
from datetime import datetime, timedelta

class AngelOneError(Exception):
    """Custom exception for Angel One API errors"""
    
    ERROR_CODES = {
        "AG8001": "Invalid Token",
        "AG8002": "Token Expired", 
        "AG8003": "Token missing",
        "AB8050": "Invalid Refresh Token",
        "AB8051": "Refresh Token Expired",
        "AB1000": "Invalid Email Or Password",
        "AB1001": "Invalid Email",
        "AB1002": "Invalid Password Length",
        "AB1003": "Client Already Exists",
        "AB1004": "Something Went Wrong, Please Try After Sometime",
        "AB1005": "User Type Must Be USER",
        "AB1006": "Client Is Block For Trading",
        "AB1007": "AMX Error",
        "AB1008": "Invalid Order Variety",
        "AB1009": "Symbol Not Found",
        "AB1010": "AMX Session Expired",
        "AB1011": "Client not login",
        "AB1012": "Invalid Product Type",
        "AB1013": "Order not found",
        "AB1014": "Trade not found",
        "AB1015": "Holding not found",
        "AB1016": "Position not found",
        "AB1017": "Position conversion failed",
        "AB1018": "Failed to get symbol details",
        "AB2000": "Error not specified",
        "AB2001": "Internal Error, Please try after sometime",
        "AB1031": "Old Password Mismatch",
        "AB1032": "User Not Found",
        "AB2002": "ROBO order is block",
        "AB4008": "ordertag length should be less than 20 characters"
    }
    
    def __init__(self, error_code: str, message: str = None):
        self.error_code = error_code
        self.message = message or self.ERROR_CODES.get(error_code, "Unknown error")
        super().__init__(f"{error_code}: {self.message}")

class AuthenticationManager:
    """Manages Angel One API authentication and token refresh"""
    
    def __init__(self, api_key: str, client_code: str, password: str, totp_token: str):
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.totp_token = totp_token
        self.smart_api = SmartConnect(api_key)
        self.auth_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.feed_token: Optional[str] = None
        self.session_expiry: Optional[datetime] = None
        
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Angel One API and get tokens"""
        try:
            # Generate TOTP
            totp = pyotp.TOTP(self.totp_token).now()
            logger.info("Generated TOTP for authentication")
            
            # Generate session using SmartAPI library
            # The library handles the REST API call to /rest/auth/angelbroking/user/v1/loginByPassword
            data = self.smart_api.generateSession(self.client_code, self.password, totp)
            
            # Check if authentication was successful
            if not data.get('status', False) and not data.get('success', False):
                error_code = data.get('errorcode') or data.get('errorCode', 'AB2000')
                error_message = data.get('message', 'Authentication failed')
                logger.error(f"Authentication failed: {error_code} - {error_message}")
                raise AngelOneError(error_code, error_message)
            
            # Extract tokens from response
            session_data = data['data']
            self.auth_token = session_data['jwtToken']
            self.refresh_token = session_data['refreshToken']
            self.feed_token = session_data.get('feedToken') or self.smart_api.getfeedToken()
            
            # Set session expiry (Angel One sessions last up to 28 hours)
            self.session_expiry = datetime.now() + timedelta(hours=27)
            
            logger.info("Successfully authenticated with Angel One API")
            return {
                "status": "success",
                "auth_token": self.auth_token,
                "refresh_token": self.refresh_token,
                "feed_token": self.feed_token,
                "expires_at": self.session_expiry.isoformat()
            }
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Authentication error: {str(e)}")
            raise AngelOneError("AB2001", f"Authentication failed: {str(e)}")
    
    async def refresh_session(self) -> bool:
        """Refresh the authentication session"""
        try:
            if not self.refresh_token:
                logger.warning("No refresh token available, need to re-authenticate")
                return False
            
            # Generate new token using refresh token
            result = self.smart_api.generateToken(self.refresh_token)
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB8050')
                logger.error(f"Token refresh failed: {error_code}")
                raise AngelOneError(error_code)
            
            # Update session expiry
            self.session_expiry = datetime.now() + timedelta(hours=23)
            logger.info("Successfully refreshed authentication token")
            return True
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not self.auth_token or not self.session_expiry:
            return False
        
        # Check if session expires in next 5 minutes
        return datetime.now() < (self.session_expiry - timedelta(minutes=5))
    
    async def ensure_valid_session(self) -> bool:
        """Ensure we have a valid session, refresh if needed"""
        if self.is_session_valid():
            return True
        
        logger.info("Session expired or expiring soon, attempting refresh")
        if await self.refresh_session():
            return True
        
        logger.info("Token refresh failed, re-authenticating")
        try:
            await self.authenticate()
            return True
        except Exception as e:
            logger.error(f"Re-authentication failed: {str(e)}")
            return False

class AngelOneClient:
    """Angel One SmartAPI client for option chain and market data"""
    
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE") 
        self.password = os.getenv("ANGEL_PASSWORD")
        self.totp_token = os.getenv("ANGEL_TOTP_TOKEN")
        
        if not all([self.api_key, self.client_code, self.password, self.totp_token]):
            raise ValueError("Missing required Angel One API credentials in environment variables")
        
        self.auth_manager = AuthenticationManager(
            self.api_key, self.client_code, self.password, self.totp_token
        )
        self.websocket_client: Optional[SmartWebSocketV2] = None
        
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Angel One API"""
        return await self.auth_manager.authenticate()
    
    async def ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        return await self.auth_manager.ensure_valid_session()
    
    def get_smart_api(self) -> SmartConnect:
        """Get the SmartConnect instance"""
        return self.auth_manager.smart_api
    
    def get_auth_token(self) -> Optional[str]:
        """Get current auth token"""
        return self.auth_manager.auth_token
    
    def get_feed_token(self) -> Optional[str]:
        """Get current feed token"""
        return self.auth_manager.feed_token
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            if not await self.ensure_authenticated():
                raise AngelOneError("AB1011", "Authentication required")
            
            smart_api = self.get_smart_api()
            result = smart_api.getProfile(self.auth_manager.refresh_token)
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB2000')
                raise AngelOneError(error_code, result.get('message'))
            
            return result['data']
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Profile fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch profile: {str(e)}")
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        try:
            if not await self.ensure_authenticated():
                raise AngelOneError("AB1011", "Authentication required")
            
            smart_api = self.get_smart_api()
            
            # Use LTP API to get current price
            # For NIFTY and BANKNIFTY, we need to use the index tokens
            symbol_tokens = {
                "NIFTY": "99926000",  # NIFTY 50 token
                "BANKNIFTY": "99926009"  # BANK NIFTY token
            }
            
            if symbol not in symbol_tokens:
                raise ValueError(f"Unsupported symbol: {symbol}")
            
            # Get LTP (Last Traded Price)
            ltp_data = {
                "exchange": "NSE",
                "tradingsymbol": symbol,
                "symboltoken": symbol_tokens[symbol]
            }
            
            result = smart_api.ltpData("NSE", symbol, symbol_tokens[symbol])
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB2000')
                raise AngelOneError(error_code, result.get('message'))
            
            return float(result['data']['ltp'])
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Current price fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch current price: {str(e)}")
    
    async def get_nearest_expiry(self, symbol: str) -> str:
        """Get the nearest expiry date for the symbol"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        if symbol == "NIFTY":
            # NIFTY has weekly expiries on Thursdays
            days_ahead = 3 - today.weekday()  # Thursday is 3
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            next_thursday = today + timedelta(days=days_ahead)
            return f"{next_thursday.day:02d}{months[next_thursday.month-1]}{next_thursday.year}"
            
        elif symbol == "BANKNIFTY":
            # BANKNIFTY has monthly expiries - last Thursday of the month
            # For simplicity, let's use the current month's last Thursday or next month's
            current_month = today.month
            current_year = today.year
            
            # Try current month's last Thursday first
            # Get last day of current month
            if current_month == 12:
                next_month = 1
                next_year = current_year + 1
            else:
                next_month = current_month + 1
                next_year = current_year
            
            # Last day of current month
            last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
            
            # Find last Thursday of current month
            days_back = (last_day.weekday() - 3) % 7
            last_thursday = last_day - timedelta(days=days_back)
            
            # If last Thursday has passed, use next month's last Thursday
            if last_thursday < today:
                if next_month == 12:
                    next_next_month = 1
                    next_next_year = next_year + 1
                else:
                    next_next_month = next_month + 1
                    next_next_year = next_year
                
                # Last day of next month
                last_day_next = datetime(next_next_year, next_next_month, 1) - timedelta(days=1)
                days_back = (last_day_next.weekday() - 3) % 7
                last_thursday = last_day_next - timedelta(days=days_back)
            
            return f"{last_thursday.day:02d}{months[last_thursday.month-1]}{last_thursday.year}"
        
        else:
            # Default to next Thursday for other symbols
            days_ahead = 3 - today.weekday()  # Thursday is 3
            if days_ahead <= 0:
                days_ahead += 7
            
            next_thursday = today + timedelta(days=days_ahead)
            return f"{next_thursday.day:02d}{months[next_thursday.month-1]}{next_thursday.year}"
    
    async def get_option_greeks(self, symbol: str, expiry_date: str = None) -> List[Dict[str, Any]]:
        """Fetch option Greeks data for given symbol and expiry"""
        try:
            if not await self.ensure_authenticated():
                raise AngelOneError("AB1011", "Authentication required")
            
            # If no expiry provided, get nearest expiry
            if not expiry_date:
                expiry_date = await self.get_nearest_expiry(symbol)
            
            smart_api = self.get_smart_api()
            
            # Call the option Greeks API
            # This uses the endpoint: /rest/secure/angelbroking/marketData/v1/optionGreek
            request_data = {
                "name": symbol,
                "expirydate": expiry_date
            }
            
            result = smart_api.optionGreek(request_data)
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB2000')
                raise AngelOneError(error_code, result.get('message'))
            
            return result['data']
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Option Greeks fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch option Greeks: {str(e)}")
    
    async def get_relevant_option_strikes(self, symbol: str, strikes_range: int = 5) -> List[Dict[str, Any]]:
        """Get option Greeks for strikes around current market price"""
        try:
            # Get current market price
            current_price = await self.get_current_price(symbol)
            logger.info(f"Current {symbol} price: {current_price}")
            
            # Get all option Greeks for nearest expiry
            expiry_date = await self.get_nearest_expiry(symbol)
            all_options = await self.get_option_greeks(symbol, expiry_date)
            
            if not all_options:
                return []
            
            # Determine strike interval based on symbol
            strike_interval = 50 if symbol == "NIFTY" else 100  # BANKNIFTY typically has 100 point intervals
            
            # Find the ATM strike (closest to current price)
            atm_strike = round(current_price / strike_interval) * strike_interval
            
            # Calculate the strikes we want (5 above and 5 below ATM)
            target_strikes = []
            for i in range(-strikes_range, strikes_range + 1):
                target_strikes.append(atm_strike + (i * strike_interval))
            
            # Filter options to only include our target strikes
            relevant_options = []
            for option in all_options:
                strike_price = float(option['strikePrice'])
                if strike_price in target_strikes:
                    relevant_options.append(option)
            
            # Sort by strike price and option type
            relevant_options.sort(key=lambda x: (float(x['strikePrice']), x['optionType']))
            
            logger.info(f"Found {len(relevant_options)} relevant options for {symbol}")
            return relevant_options
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Relevant strikes fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch relevant strikes: {str(e)}")
    
    async def get_top_gainers_losers(self, data_type: str, expiry_type: str = "NEAR") -> List[Dict[str, Any]]:
        """Fetch top gainers/losers data for derivatives"""
        try:
            if not await self.ensure_authenticated():
                raise AngelOneError("AB1011", "Authentication required")
            
            # Validate data_type
            valid_data_types = ["PercPriceGainers", "PercPriceLosers", "PercOIGainers", "PercOILosers"]
            if data_type not in valid_data_types:
                raise ValueError(f"Invalid data_type. Must be one of: {valid_data_types}")
            
            # Validate expiry_type
            valid_expiry_types = ["NEAR", "NEXT", "FAR"]
            if expiry_type not in valid_expiry_types:
                raise ValueError(f"Invalid expiry_type. Must be one of: {valid_expiry_types}")
            
            smart_api = self.get_smart_api()
            
            # Call the top gainers/losers API
            # This uses the endpoint: /rest/secure/angelbroking/marketData/v1/gainersLosers
            request_data = {
                "datatype": data_type,
                "expirytype": expiry_type
            }
            
            result = smart_api.gainersLosers(request_data)
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB2000')
                raise AngelOneError(error_code, result.get('message'))
            
            return result['data']
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Top gainers/losers fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch top gainers/losers: {str(e)}")
    
    async def get_ohlc_data(self, exchange: str, symbol_token: str, interval: str = "ONE_MINUTE", 
                           from_date: str = None, to_date: str = None) -> List[List]:
        """Fetch historical OHLC data for charts"""
        try:
            if not await self.ensure_authenticated():
                raise AngelOneError("AB1011", "Authentication required")
            
            smart_api = self.get_smart_api()
            
            # Set default dates if not provided (last 7 days)
            if not from_date or not to_date:
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                from_date = start_date.strftime("%Y-%m-%d %H:%M")
                to_date = end_date.strftime("%Y-%m-%d %H:%M")
            
            # Call the historical data API
            # This uses the endpoint: /rest/secure/angelbroking/historical/v1/getCandleData
            historic_param = {
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            result = smart_api.getCandleData(historic_param)
            
            if result.get('status') == False:
                error_code = result.get('errorcode', 'AB2000')
                raise AngelOneError(error_code, result.get('message'))
            
            return result['data']
            
        except Exception as e:
            if isinstance(e, AngelOneError):
                raise
            logger.error(f"Historical data fetch error: {str(e)}")
            raise AngelOneError("AB2001", f"Failed to fetch historical data: {str(e)}")
    
    async def logout(self):
        """Logout and terminate the session"""
        try:
            if not await self.ensure_authenticated():
                logger.warning("No active session to logout")
                return {"status": "success", "message": "No active session"}
            
            smart_api = self.get_smart_api()
            result = smart_api.terminateSession(self.client_code)
            
            # Clear tokens
            self.auth_manager.auth_token = None
            self.auth_manager.refresh_token = None
            self.auth_manager.feed_token = None
            self.auth_manager.session_expiry = None
            
            # Close WebSocket if open
            if self.websocket_client:
                self.close_websocket()
                self.websocket_client = None
            
            logger.info("Successfully logged out from Angel One API")
            return {"status": "success", "message": "Logout successful"}
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise AngelOneError("AB2001", f"Logout failed: {str(e)}")