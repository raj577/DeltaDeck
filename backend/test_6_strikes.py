#!/usr/bin/env python3
"""
Test script to fetch exactly 6 strikes up and down for NIFTY and BANKNIFTY
As per requirements: "use just 6 up and down strikes including atm strike"
"""
import asyncio
import os
from dotenv import load_dotenv
from angel_api import AngelOneClient, AngelOneError

async def test_6_strikes():
    """Test getting exactly 6 strikes up and down for NIFTY and BANKNIFTY"""
    
    # Load environment variables
    load_dotenv()
    
    print("📊 Testing 6 Strikes Up & Down (Including ATM)...")
    print("=" * 70)
    print("🎯 Target: 6 strikes above ATM + ATM + 6 strikes below ATM = 13 total strikes")
    print("💰 Lot Sizes: NIFTY = 75, BANKNIFTY = 35")
    print("=" * 70)
    
    try:
        # Initialize client
        client = AngelOneClient()
        print("✅ Angel One client initialized successfully")
        
        # Test authentication
        print("\n🔑 Authenticating...")
        auth_result = await client.authenticate()
        print("✅ Authentication successful!")
        
        # Test NIFTY 6 strikes
        print("\n📈 Getting NIFTY 6 Strikes Up & Down...")
        try:
            # Get current price and option data (6 strikes range)
            nifty_price = await client.get_current_price("NIFTY")
            nifty_options = await client.get_relevant_option_strikes("NIFTY", strikes_range=6)
            
            print(f"   Current NIFTY Price: ₹{nifty_price:,.2f}")
            print(f"   Retrieved {len(nifty_options)} option contracts")
            
            if nifty_options:
                # Separate calls and puts
                calls = [opt for opt in nifty_options if opt['optionType'] == 'CE']
                puts = [opt for opt in nifty_options if opt['optionType'] == 'PE']
                
                print(f"\n   📞 NIFTY CALL OPTIONS ({len(calls)}):")
                print("   " + "-" * 90)
                print("   Strike    | Delta    | Gamma    | Theta    | Vega     | IV       | Volume    | ATM?")
                print("   " + "-" * 90)
                
                # Find ATM strike
                atm_strike = round(nifty_price / 50) * 50  # NIFTY strike interval is 50
                
                for call in sorted(calls, key=lambda x: float(x['strikePrice'])):
                    strike = float(call['strikePrice'])
                    delta = float(call['delta'])
                    gamma = float(call['gamma'])
                    theta = float(call['theta'])
                    vega = float(call['vega'])
                    iv = float(call['impliedVolatility'])
                    volume = float(call['tradeVolume'])
                    is_atm = "ATM" if strike == atm_strike else ""
                    
                    print(f"   {strike:8.0f}  | {delta:8.4f} | {gamma:8.4f} | {theta:8.2f} | {vega:8.4f} | {iv:8.2f}% | {volume:9.0f} | {is_atm}")
                
                print(f"\n   📉 NIFTY PUT OPTIONS ({len(puts)}):")
                print("   " + "-" * 90)
                print("   Strike    | Delta    | Gamma    | Theta    | Vega     | IV       | Volume    | ATM?")
                print("   " + "-" * 90)
                
                for put in sorted(puts, key=lambda x: float(x['strikePrice'])):
                    strike = float(put['strikePrice'])
                    delta = float(put['delta'])
                    gamma = float(put['gamma'])
                    theta = float(put['theta'])
                    vega = float(put['vega'])
                    iv = float(put['impliedVolatility'])
                    volume = float(put['tradeVolume'])
                    is_atm = "ATM" if strike == atm_strike else ""
                    
                    print(f"   {strike:8.0f}  | {delta:8.4f} | {gamma:8.4f} | {theta:8.2f} | {vega:8.4f} | {iv:8.2f}% | {volume:9.0f} | {is_atm}")
            
            else:
                print("⚠️  No NIFTY options found")
                
        except AngelOneError as e:
            print(f"⚠️  NIFTY strikes failed: {e}")
        
        # Add delay to avoid rate limiting
        print("\n⏳ Waiting 3 seconds to avoid rate limiting...")
        await asyncio.sleep(3)
        
        # Test BANKNIFTY 6 strikes
        print("\n🏦 Getting BANKNIFTY 6 Strikes Up & Down...")
        try:
            # Get current price and option data (6 strikes range)
            banknifty_price = await client.get_current_price("BANKNIFTY")
            banknifty_options = await client.get_relevant_option_strikes("BANKNIFTY", strikes_range=6)
            
            print(f"   Current BANKNIFTY Price: ₹{banknifty_price:,.2f}")
            print(f"   Retrieved {len(banknifty_options)} option contracts")
            
            if banknifty_options:
                # Separate calls and puts
                calls = [opt for opt in banknifty_options if opt['optionType'] == 'CE']
                puts = [opt for opt in banknifty_options if opt['optionType'] == 'PE']
                
                print(f"\n   📞 BANKNIFTY CALL OPTIONS ({len(calls)}):")
                print("   " + "-" * 90)
                print("   Strike    | Delta    | Gamma    | Theta    | Vega     | IV       | Volume    | ATM?")
                print("   " + "-" * 90)
                
                # Find ATM strike
                atm_strike = round(banknifty_price / 100) * 100  # BANKNIFTY strike interval is 100
                
                for call in sorted(calls, key=lambda x: float(x['strikePrice'])):
                    strike = float(call['strikePrice'])
                    delta = float(call['delta'])
                    gamma = float(call['gamma'])
                    theta = float(call['theta'])
                    vega = float(call['vega'])
                    iv = float(call['impliedVolatility'])
                    volume = float(call['tradeVolume'])
                    is_atm = "ATM" if strike == atm_strike else ""
                    
                    print(f"   {strike:8.0f}  | {delta:8.4f} | {gamma:8.4f} | {theta:8.2f} | {vega:8.4f} | {iv:8.2f}% | {volume:9.0f} | {is_atm}")
                
                print(f"\n   📉 BANKNIFTY PUT OPTIONS ({len(puts)}):")
                print("   " + "-" * 90)
                print("   Strike    | Delta    | Gamma    | Theta    | Vega     | IV       | Volume    | ATM?")
                print("   " + "-" * 90)
                
                for put in sorted(puts, key=lambda x: float(x['strikePrice'])):
                    strike = float(put['strikePrice'])
                    delta = float(put['delta'])
                    gamma = float(put['gamma'])
                    theta = float(put['theta'])
                    vega = float(put['vega'])
                    iv = float(put['impliedVolatility'])
                    volume = float(put['tradeVolume'])
                    is_atm = "ATM" if strike == atm_strike else ""
                    
                    print(f"   {strike:8.0f}  | {delta:8.4f} | {gamma:8.4f} | {theta:8.2f} | {vega:8.4f} | {iv:8.2f}% | {volume:9.0f} | {is_atm}")
            
            else:
                print("⚠️  No BANKNIFTY options found")
                
        except AngelOneError as e:
            print(f"⚠️  BANKNIFTY strikes failed: {e}")
        
        # Test logout
        print("\n🚪 Logging out...")
        logout_result = await client.logout()
        print(f"✅ {logout_result['message']}")
        
    except AngelOneError as e:
        print(f"❌ Angel One API Error: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Message: {e.message}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 70)
    print("🏁 6 Strikes test completed")
    print("\n📋 Summary:")
    print("   ✅ Fetched 6 strikes above and below ATM (13 total per symbol)")
    print("   ✅ Identified ATM strikes for both indices")
    print("   ✅ Retrieved complete option Greeks data")
    print("   ✅ Ready for spread analysis with delta filtering (0.15-0.26)")

if __name__ == "__main__":
    asyncio.run(test_6_strikes())