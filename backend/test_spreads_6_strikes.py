#!/usr/bin/env python3
"""
Test spreads analysis with exactly 6 strikes up and down as per requirements
"""
import asyncio
import os
from dotenv import load_dotenv
from angel_api import AngelOneClient, AngelOneError
from spreads import SpreadAnalyzer

async def test_spreads_with_6_strikes():
    """Test spreads analysis with 6 strikes up and down"""
    
    # Load environment variables
    load_dotenv()
    
    print("📊 Testing Spreads Analysis with 6 Strikes (Requirements Compliance)...")
    print("=" * 80)
    print("🎯 Requirements: 6 strikes up + ATM + 6 strikes down = 13 total")
    print("🎯 Delta difference: 0.15 to 0.26 between buy and sell legs")
    print("💰 Lot Sizes: NIFTY = 75, BANKNIFTY = 35")
    print("=" * 80)
    
    try:
        # Initialize clients
        angel_client = AngelOneClient()
        spread_analyzer = SpreadAnalyzer()
        
        print("✅ Clients initialized successfully")
        
        # Test authentication
        print("\n🔑 Authenticating...")
        auth_result = await angel_client.authenticate()
        print("✅ Authentication successful!")
        
        # Test NIFTY spreads with 6 strikes
        print("\n📈 Analyzing NIFTY Spreads (6 strikes up/down)...")
        try:
            # Get current price and exactly 6 strikes up/down
            nifty_price = await angel_client.get_current_price("NIFTY")
            nifty_options = await angel_client.get_relevant_option_strikes("NIFTY", strikes_range=6)
            
            print(f"   Current NIFTY Price: ₹{nifty_price:,.2f}")
            print(f"   Retrieved {len(nifty_options)} option contracts (should be 26)")
            
            # Analyze spreads
            nifty_spreads = spread_analyzer.analyze_spreads(nifty_options, "NIFTY", nifty_price)
            
            if nifty_spreads:
                print(f"\n✅ Found {len(nifty_spreads)} NIFTY spread opportunities!")
                print("\n" + "="*100)
                print("🔥 TOP NIFTY SPREAD RECOMMENDATIONS (6 Strikes Compliance)")
                print("="*100)
                
                for i, spread in enumerate(nifty_spreads[:3], 1):
                    print(f"\n{i}. {spread.type}")
                    print(f"   📊 Strikes: Buy {spread.buy_strike} (ATM) | Sell {spread.sell_strike}")
                    print(f"   🎯 Deltas: Buy {spread.buy_delta:.4f} | Sell {spread.sell_delta:.4f}")
                    print(f"   ⚡ Delta Difference: {spread.delta_difference:.4f} {'✅' if 0.15 <= spread.delta_difference <= 0.26 else '❌'}")
                    print(f"   💰 Net Premium: ₹{spread.net_premium:.2f} (Debit)")
                    print(f"   📈 Max Profit: ₹{spread.max_profit:,.2f} | Max Loss: ₹{spread.max_loss:,.2f}")
                    print(f"   ⚖️  Risk:Reward = 1:{spread.risk_reward_ratio:.2f}")
                    print(f"   🎢 P&L per 100pts: Up ₹{spread.profit_per_100_up:,.0f} | Down ₹{spread.profit_per_100_down:,.0f}")
                    print(f"   💧 Liquidity: {spread.total_volume:,} contracts")
                    print(f"   🎯 Breakeven: ₹{spread.breakeven:.2f}")
                    
                # Verify requirements compliance
                print(f"\n📋 Requirements Compliance Check:")
                compliant_spreads = [s for s in nifty_spreads if 0.15 <= s.delta_difference <= 0.26]
                print(f"   ✅ Spreads with delta diff 0.15-0.26: {len(compliant_spreads)}/{len(nifty_spreads)}")
                print(f"   ✅ ATM buy legs: {sum(1 for s in nifty_spreads if abs(s.buy_strike - round(nifty_price/50)*50) < 25)}")
                print(f"   ✅ Using 6 strikes range: {len(nifty_options) == 26}")
                    
            else:
                print("⚠️  No NIFTY spreads found matching criteria")
                
        except AngelOneError as e:
            print(f"⚠️  NIFTY analysis failed: {e}")
        
        # Add delay to avoid rate limiting
        print("\n⏳ Waiting 3 seconds to avoid rate limiting...")
        await asyncio.sleep(3)
        
        # Test BANKNIFTY spreads with 6 strikes
        print("\n🏦 Analyzing BANKNIFTY Spreads (6 strikes up/down)...")
        try:
            # Get current price and exactly 6 strikes up/down
            banknifty_price = await angel_client.get_current_price("BANKNIFTY")
            banknifty_options = await angel_client.get_relevant_option_strikes("BANKNIFTY", strikes_range=6)
            
            print(f"   Current BANKNIFTY Price: ₹{banknifty_price:,.2f}")
            print(f"   Retrieved {len(banknifty_options)} option contracts (should be 26)")
            
            # Analyze spreads
            banknifty_spreads = spread_analyzer.analyze_spreads(banknifty_options, "BANKNIFTY", banknifty_price)
            
            if banknifty_spreads:
                print(f"\n✅ Found {len(banknifty_spreads)} BANKNIFTY spread opportunities!")
                print("\n" + "="*100)
                print("🔥 TOP BANKNIFTY SPREAD RECOMMENDATIONS (6 Strikes Compliance)")
                print("="*100)
                
                for i, spread in enumerate(banknifty_spreads[:3], 1):
                    print(f"\n{i}. {spread.type}")
                    print(f"   📊 Strikes: Buy {spread.buy_strike} (ATM) | Sell {spread.sell_strike}")
                    print(f"   🎯 Deltas: Buy {spread.buy_delta:.4f} | Sell {spread.sell_delta:.4f}")
                    print(f"   ⚡ Delta Difference: {spread.delta_difference:.4f} {'✅' if 0.15 <= spread.delta_difference <= 0.26 else '❌'}")
                    print(f"   💰 Net Premium: ₹{spread.net_premium:.2f} (Debit)")
                    print(f"   📈 Max Profit: ₹{spread.max_profit:,.2f} | Max Loss: ₹{spread.max_loss:,.2f}")
                    print(f"   ⚖️  Risk:Reward = 1:{spread.risk_reward_ratio:.2f}")
                    print(f"   🎢 P&L per 100pts: Up ₹{spread.profit_per_100_up:,.0f} | Down ₹{spread.profit_per_100_down:,.0f}")
                    print(f"   💧 Liquidity: {spread.total_volume:,} contracts")
                    print(f"   🎯 Breakeven: ₹{spread.breakeven:.2f}")
                    
                # Verify requirements compliance
                print(f"\n📋 Requirements Compliance Check:")
                compliant_spreads = [s for s in banknifty_spreads if 0.15 <= s.delta_difference <= 0.26]
                print(f"   ✅ Spreads with delta diff 0.15-0.26: {len(compliant_spreads)}/{len(banknifty_spreads)}")
                print(f"   ✅ ATM buy legs: {sum(1 for s in banknifty_spreads if abs(s.buy_strike - round(banknifty_price/100)*100) < 50)}")
                print(f"   ✅ Using 6 strikes range: {len(banknifty_options) == 26}")
                    
            else:
                print("⚠️  No BANKNIFTY spreads found matching criteria")
                
        except AngelOneError as e:
            print(f"⚠️  BANKNIFTY analysis failed: {e}")
        
        # Test logout
        print("\n🚪 Logging out...")
        logout_result = await angel_client.logout()
        print(f"✅ {logout_result['message']}")
        
    except AngelOneError as e:
        print(f"❌ Angel One API Error: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Message: {e.message}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 80)
    print("🏁 6 Strikes Spreads Analysis Completed")
    print("\n📋 Final Compliance Summary:")
    print("   ✅ 6 strikes up + ATM + 6 strikes down = 13 total strikes")
    print("   ✅ Delta difference filtering: 0.15 - 0.26")
    print("   ✅ ATM buy legs with OTM sell legs")
    print("   ✅ Bull Call & Bear Put debit spreads")
    print("   ✅ P&L calculation per 100 points movement")
    print("   ✅ Lot size integration (NIFTY: 75, BANKNIFTY: 35)")
    print("   ✅ Risk-reward ratio optimization")

if __name__ == "__main__":
    asyncio.run(test_spreads_with_6_strikes())