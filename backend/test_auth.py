#!/usr/bin/env python3
"""
Test script to verify Angel One API authentication with real credentials
"""
import asyncio
import os
from dotenv import load_dotenv
from angel_api import AngelOneClient, AngelOneError

async def test_authentication():
    """Test real authentication with Angel One API"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔐 Testing Angel One API Authentication...")
    print("=" * 50)
    
    try:
        # Initialize client
        client = AngelOneClient()
        print("✅ Angel One client initialized successfully")
        
        # Test authentication
        print("\n🔑 Attempting authentication...")
        auth_result = await client.authenticate()
        
        if auth_result['status'] == 'success':
            print("✅ Authentication successful!")
            print(f"   Auth Token: {auth_result['auth_token'][:20]}...")
            print(f"   Feed Token: {auth_result['feed_token'][:20]}...")
            print(f"   Expires At: {auth_result['expires_at']}")
            
            # Test profile fetch (skip if trading blocked)
            print("\n👤 Attempting to fetch user profile...")
            try:
                profile = await client.get_profile()
                print("✅ Profile fetched successfully!")
                print(f"   Client Code: {profile['clientcode']}")
                print(f"   Name: {profile['name']}")
                print(f"   Email: {profile['email']}")
                print(f"   Exchanges: {profile['exchanges']}")
            except AngelOneError as e:
                print(f"⚠️  Profile fetch failed (expected if trading blocked): {e.error_code}")
            
            # Test current prices
            print("\n💰 Testing current prices...")
            try:
                nifty_price = await client.get_current_price("NIFTY")
                banknifty_price = await client.get_current_price("BANKNIFTY")
                print(f"✅ NIFTY: ₹{nifty_price:,.2f}")
                print(f"✅ BANKNIFTY: ₹{banknifty_price:,.2f}")
            except AngelOneError as e:
                print(f"⚠️  Price fetch failed: {e}")
            
            # Test option Greeks (sample)
            print("\n📊 Testing Option Greeks API...")
            try:
                # Try current month expiry - format should be like "25JUL2025" for July 2025
                from datetime import datetime
                current_date = datetime.now()
                # Try next Thursday (typical option expiry)
                expiry_date = "01AUG2025"  # Try August 2025 expiry
                
                greeks = await client.get_option_greeks("NIFTY", expiry_date)
                print(f"✅ Option Greeks fetched successfully! Found {len(greeks)} options")
                if greeks:
                    sample = greeks[0]
                    print(f"   Sample: {sample['name']} {sample['strikePrice']} {sample['optionType']}")
                    print(f"   Delta: {sample['delta']}, Gamma: {sample['gamma']}")
            except AngelOneError as e:
                print(f"⚠️  Option Greeks test failed: {e}")
                # Try alternative expiry format
                try:
                    greeks = await client.get_option_greeks("NIFTY", "18JUL2025")
                    print(f"✅ Option Greeks (alt format) fetched! Found {len(greeks)} options")
                except AngelOneError as e2:
                    print(f"⚠️  Alternative expiry also failed: {e2}")
            
            # Test top gainers/losers
            print("\n📈 Testing Top Gainers API...")
            try:
                gainers = await client.get_top_gainers_losers("PercOIGainers", "NEAR")
                print(f"✅ Top Gainers fetched successfully! Found {len(gainers)} items")
                if gainers:
                    sample = gainers[0]
                    print(f"   Top Gainer: {sample['tradingSymbol']}")
                    print(f"   Percent Change: {sample['percentChange']}%")
            except AngelOneError as e:
                print(f"⚠️  Top Gainers test failed: {e}")
            
            # Test historical data
            print("\n📊 Testing Historical Data API...")
            try:
                # NIFTY 50 token for NSE
                historical_data = await client.get_ohlc_data("NSE", "99926000", "ONE_MINUTE")
                print(f"✅ Historical data fetched successfully! Found {len(historical_data)} candles")
                if historical_data:
                    sample = historical_data[0]
                    print(f"   Sample candle: Open={sample[1]}, High={sample[2]}, Low={sample[3]}, Close={sample[4]}")
            except AngelOneError as e:
                print(f"⚠️  Historical data test failed: {e}")
            
            # Test logout
            print("\n🚪 Testing logout...")
            logout_result = await client.logout()
            print(f"✅ {logout_result['message']}")
            
        else:
            print("❌ Authentication failed!")
            
    except AngelOneError as e:
        print(f"❌ Angel One API Error: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Message: {e.message}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    print("\n" + "=" * 50)
    print("🏁 Authentication test completed")

if __name__ == "__main__":
    asyncio.run(test_authentication())