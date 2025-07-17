# FastAPI main application file
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio
import time
import json
import struct
import websockets
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Set
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Import our modules
from angel_api import AngelOneClient, AngelOneError
from spreads import SpreadAnalyzer, SpreadRecommendation
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Global clients (will be initialized on startup)
angel_client: Optional[AngelOneClient] = None
spread_analyzer: Optional[SpreadAnalyzer] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.price_task: Optional[asyncio.Task] = None
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket client connected. Total connections: {len(self.active_connections)}")
        
        # Start price streaming if this is the first connection
        if len(self.active_connections) == 1:
            await self.start_price_streaming()
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"❌ WebSocket client disconnected. Total connections: {len(self.active_connections)}")
            
            # Stop price streaming if no connections left
            if len(self.active_connections) == 0:
                self.stop_price_streaming()
    
    async def broadcast_prices(self, data: dict):
        """Broadcast price data to all connected clients"""
        if self.active_connections:
            message = json.dumps({
                "type": "price_update",
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send to all connected clients
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"❌ Error sending to WebSocket client: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection)
    
    async def start_price_streaming(self):
        """Start the background task for price streaming"""
        if not self.price_task or self.price_task.done():
            print("🚀 Starting real-time price streaming...")
            self.price_task = asyncio.create_task(self.price_streaming_loop())
    
    def stop_price_streaming(self):
        """Stop the background task for price streaming"""
        if self.price_task and not self.price_task.done():
            print("🛑 Stopping real-time price streaming...")
            self.price_task.cancel()
    
    async def price_streaming_loop(self):
        """Background loop to connect to Angel One WebSocket and stream prices"""
        import websockets
        import struct
        
        while True:
            try:
                if angel_client and len(self.active_connections) > 0:
                    print("🔌 Connecting to Angel One WebSocket...")
                    
                    # Get auth details from angel_client
                    auth_token = angel_client.get_auth_token()
                    api_key = angel_client.api_key
                    client_code = angel_client.client_code
                    feed_token = angel_client.get_feed_token()
                    
                    if not all([auth_token, api_key, client_code, feed_token]):
                        print("❌ Missing WebSocket authentication details")
                        await asyncio.sleep(10)
                        continue
                    
                    # WebSocket URL with query params for browser compatibility
                    ws_url = f"wss://smartapisocket.angelone.in/smart-stream?clientCode={client_code}&feedToken={feed_token}&apiKey={api_key}"
                    
                    headers = {
                        "Authorization": f"Bearer {auth_token}",
                        "x-api-key": api_key,
                        "x-client-code": client_code,
                        "x-feed-token": feed_token
                    }
                    
                    async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                        print("✅ Connected to Angel One WebSocket")
                        
                        # Subscribe to NIFTY and BANKNIFTY LTP
                        subscribe_request = {
                            "correlationID": "price_feed",
                            "action": 1,  # Subscribe
                            "params": {
                                "mode": 1,  # LTP mode
                                "tokenList": [
                                    {
                                        "exchangeType": 1,  # NSE_CM
                                        "tokens": ["99926000", "99926009"]  # NIFTY, BANKNIFTY
                                    }
                                ]
                            }
                        }
                        
                        await websocket.send(json.dumps(subscribe_request))
                        print("📡 Subscribed to NIFTY and BANKNIFTY LTP feed")
                        
                        # Start heartbeat task
                        heartbeat_task = asyncio.create_task(self.send_heartbeat(websocket))
                        
                        try:
                            async for message in websocket:
                                if isinstance(message, bytes):
                                    # Parse binary message
                                    price_data = self.parse_angel_websocket_data(message)
                                    if price_data:
                                        await self.broadcast_prices(price_data)
                                else:
                                    # Handle text messages (like pong)
                                    if message == "pong":
                                        print("💓 Heartbeat acknowledged")
                        finally:
                            heartbeat_task.cancel()
                            
            except asyncio.CancelledError:
                print("🛑 Price streaming task cancelled")
                break
            except Exception as e:
                print(f"❌ Error in Angel One WebSocket: {e}")
                await asyncio.sleep(10)  # Wait before reconnecting
    
    async def send_heartbeat(self, websocket):
        """Send heartbeat every 30 seconds"""
        try:
            while True:
                await asyncio.sleep(30)
                await websocket.send("ping")
                print("💓 Sent heartbeat")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Heartbeat error: {e}")
    
    def parse_angel_websocket_data(self, data):
        """Parse Angel One WebSocket binary data"""
        try:
            if len(data) < 51:  # Minimum LTP packet size
                return None
            
            # Parse according to Angel One WebSocket specification
            mode = data[0]  # Subscription mode
            exchange_type = data[1]  # Exchange type
            
            # Extract token (25 bytes starting at position 2)
            token_bytes = data[2:27]
            token = token_bytes.decode('utf-8').rstrip('\x00')
            
            # Extract LTP (4 bytes starting at position 43)
            ltp_bytes = data[43:47]
            ltp_paise = struct.unpack('<I', ltp_bytes)[0]  # Little endian unsigned int
            ltp = ltp_paise / 100.0  # Convert paise to rupees
            
            # Map token to symbol
            symbol_map = {
                "99926000": "NIFTY",
                "99926009": "BANKNIFTY"
            }
            
            symbol = symbol_map.get(token)
            if not symbol:
                return None
            
            print(f"📊 Received {symbol}: ₹{ltp}")
            
            # Return in our standard format
            return {
                symbol: {
                    "ltp": ltp,
                    "symbol": symbol
                }
            }
            
        except Exception as e:
            print(f"❌ Error parsing WebSocket data: {e}")
            return None

# Global connection manager
manager = ConnectionManager()

# Request/Response models
class SpreadRequest(BaseModel):
    symbol: str = "NIFTY"  # NIFTY or BANKNIFTY
    strikes_range: int = 8  # Number of strikes above/below ATM

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str

class GeminiRequest(BaseModel):
    question: str

class GeminiResponse(BaseModel):
    answer: str
    timestamp: str

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global angel_client, spread_analyzer
    
    print("🚀 Starting Option Spreads Analyzer API...")
    
    # Initialize clients
    try:
        angel_client = AngelOneClient()
        spread_analyzer = SpreadAnalyzer()
        
        # Test authentication
        auth_result = await angel_client.authenticate()
        print(f"✅ Angel One authentication successful: {auth_result['status']}")
        
    except Exception as e:
        print(f"❌ Failed to initialize clients: {e}")
        # Continue anyway - we can handle auth errors per request
        angel_client = AngelOneClient()
        spread_analyzer = SpreadAnalyzer()
    
    print("✅ API startup complete!")
    
    yield  # Application runs here
    
    # Cleanup
    print("🛑 Shutting down API...")
    if angel_client:
        try:
            await angel_client.logout()
            print("✅ Angel One logout successful")
        except:
            pass
    print("✅ API shutdown complete!")

# Create FastAPI app
app = FastAPI(
    title="Option Spreads Analyzer API",
    description="Real-time option spreads analysis for NIFTY and BANKNIFTY using Angel One API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom exception handler
@app.exception_handler(AngelOneError)
async def angel_one_exception_handler(request, exc: AngelOneError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Option Spreads Analyzer API is running",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get API and Angel One connection status"""
    try:
        # Test Angel One connection
        if angel_client:
            is_authenticated = await angel_client.ensure_authenticated()
            angel_status = "connected" if is_authenticated else "disconnected"
        else:
            angel_status = "not_initialized"
        
        return {
            "api_status": "running",
            "angel_one_status": angel_status,
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time()
        }
    except Exception as e:
        return {
            "api_status": "running",
            "angel_one_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Main spreads recommendations endpoint
@app.post("/api/recommendations", response_model=List[SpreadRecommendation])
async def get_spread_recommendations(request: SpreadRequest):
    """
    Get option spread recommendations for NIFTY or BANKNIFTY
    
    Returns Bull Call and Bear Put spread recommendations with:
    - Delta difference between 0.15-0.26
    - ATM buy legs with OTM sell legs
    - P&L calculations per 100 points movement
    - Risk-reward ratios and liquidity metrics
    """
    if not angel_client or not spread_analyzer:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Validate symbol
        if request.symbol not in ["NIFTY", "BANKNIFTY"]:
            raise HTTPException(status_code=400, detail="Symbol must be NIFTY or BANKNIFTY")
        
        # Get current price
        current_price = await angel_client.get_current_price(request.symbol)
        
        # Get relevant option strikes
        option_data = await angel_client.get_relevant_option_strikes(
            request.symbol, 
            strikes_range=request.strikes_range
        )
        
        if not option_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No option data found for {request.symbol}"
            )
        
        # Analyze spreads
        spreads = spread_analyzer.analyze_spreads(option_data, request.symbol, current_price)
        
        return spreads
        
    except AngelOneError as e:
        raise HTTPException(status_code=400, detail=f"Angel One API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Quick recommendations endpoint (GET for easy testing)
@app.get("/api/recommendations/{symbol}")
async def get_quick_recommendations(symbol: str):
    """Quick GET endpoint for spread recommendations"""
    request = SpreadRequest(symbol=symbol.upper())
    return await get_spread_recommendations(request)

# Current prices endpoint
@app.get("/api/prices")
async def get_current_prices():
    """Get current prices for NIFTY and BANKNIFTY"""
    if not angel_client:
        raise HTTPException(status_code=503, detail="Angel One client not initialized")
    
    try:
        # Get both prices concurrently
        nifty_task = angel_client.get_current_price("NIFTY")
        banknifty_task = angel_client.get_current_price("BANKNIFTY")
        
        nifty_price, banknifty_price = await asyncio.gather(nifty_task, banknifty_task)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "prices": {
                "NIFTY": {
                    "ltp": nifty_price,
                    "symbol": "NIFTY"
                },
                "BANKNIFTY": {
                    "ltp": banknifty_price,
                    "symbol": "BANKNIFTY"
                }
            }
        }
        
    except AngelOneError as e:
        raise HTTPException(status_code=400, detail=f"Angel One API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Top gainers/losers endpoint
@app.get("/api/gainers-losers")
async def get_gainers_losers(
    data_type: str = "PercOIGainers",  # PercOIGainers, PercOILosers, PercPriceGainers, PercPriceLosers
    expiry_type: str = "NEAR"  # NEAR, NEXT, FAR
):
    """Get top gainers/losers in derivatives segment"""
    if not angel_client:
        raise HTTPException(status_code=503, detail="Angel One client not initialized")
    
    try:
        data = await angel_client.get_top_gainers_losers(data_type, expiry_type)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "expiry_type": expiry_type,
            "data": data
        }
        
    except AngelOneError as e:
        raise HTTPException(status_code=400, detail=f"Angel One API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Chart data endpoint
@app.get("/api/chart-data")
async def get_chart_data(
    symbol: str = "NIFTY",  # NIFTY or BANKNIFTY
    interval: str = "ONE_MINUTE",  # ONE_MINUTE, FIVE_MINUTE, etc.
    from_date: Optional[str] = None,  # YYYY-MM-DD HH:MM format
    to_date: Optional[str] = None
):
    """Get historical OHLC data for charts"""
    if not angel_client:
        raise HTTPException(status_code=503, detail="Angel One client not initialized")
    
    try:
        # Symbol token mapping
        symbol_tokens = {
            "NIFTY": "99926000",
            "BANKNIFTY": "99926009"
        }
        
        if symbol not in symbol_tokens:
            raise HTTPException(status_code=400, detail="Symbol must be NIFTY or BANKNIFTY")
        
        # Get historical data
        chart_data = await angel_client.get_ohlc_data(
            exchange="NSE",
            symbol_token=symbol_tokens[symbol],
            interval=interval,
            from_date=from_date,
            to_date=to_date
        )
        
        # Format data for frontend (Plotly.js format)
        formatted_data = []
        for candle in chart_data:
            formatted_data.append({
                "timestamp": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5] if len(candle) > 5 else 0
            })
        
        return {
            "symbol": symbol,
            "interval": interval,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(formatted_data),
            "data": formatted_data
        }
        
    except AngelOneError as e:
        raise HTTPException(status_code=400, detail=f"Angel One API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# WebSocket endpoint for real-time price streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back any messages (optional)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

# Gemini AI chat endpoint
@app.post("/api/gemini-chat", response_model=GeminiResponse)
async def gemini_chat(request: GeminiRequest):
    """Chat with Gemini AI about option spreads"""
    try:
        # Get Gemini API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyA6cZxMuNGLQkOvFcY4hff2d7BSmtmAA8c")
        
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Engineer the prompt to restrict responses to option spreads only
        engineered_prompt = f"""You are an expert AI assistant that specializes ONLY in financial option spreads (e.g., bull call spread, bear put spread, iron condor, butterfly spread, calendar spread, etc.). Your sole purpose is to answer questions clearly and concisely about these topics.

If the user asks a question about anything other than option spreads (such as specific stocks, cryptocurrencies, general news, coding, or any other unrelated topic), you MUST refuse to answer.

Your ONLY response in that case must be this exact phrase: "I can only answer questions related to option spreads."

Do not provide any other information or pleasantries if the question is off-topic.

For valid option spread questions, provide clear, educational answers that help traders understand the strategy, its risks, rewards, and when to use it.

User's question: "{request.question}" """

        # Prepare the payload for Gemini API
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": engineered_prompt}]
            }]
        }
        
        # Make the API call to Gemini
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if not response.is_success:
                raise HTTPException(status_code=response.status_code, detail=f"Gemini API error: {response.text}")
            
            result = response.json()
            
            if result.get("candidates") and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if candidate.get("content") and candidate["content"].get("parts"):
                    answer_text = candidate["content"]["parts"][0]["text"]
                    
                    return GeminiResponse(
                        answer=answer_text,
                        timestamp=datetime.now().isoformat()
                    )
            
            raise HTTPException(status_code=500, detail="Invalid response from Gemini API")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response from Gemini AI: {str(e)}")

# WebSocket info endpoint
@app.get("/api/websocket-info")
async def websocket_info():
    """Get WebSocket connection information"""
    return {
        "websocket_url": "ws://127.0.0.1:8000/ws",
        "status": "available",
        "message": "WebSocket endpoint for real-time price streaming",
        "supported_feeds": ["prices", "option_greeks", "spreads_updates"],
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )