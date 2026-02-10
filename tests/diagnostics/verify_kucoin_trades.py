
import asyncio
import os
import json
from ibis.exchange.kucoin_client import KuCoinClient

async def verify_trades():
    print("🦅 Verifying KuCoin Trade History...")
    
    # Initialize client (it loads env automatically)
    client = KuCoinClient()
    
    try:
        # Check connection
        print("   Checking connection...")
        try:
            # Simple public endpoint to verify connectivity
            await client.get_tickers() 
            print("   ✅ Connected to KuCoin API")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return

        # Fetch filled orders directly to bypass any potential client wrapper logic
        print("   Fetching recent DONE orders (fills)...")
        # KuCoin API for orders: /api/v1/orders?status=done
        data = await client._request("GET", "/api/v1/orders?status=done")
        
        items = data.get('items', [])
        print(f"   Found {len(items)} historical orders in the last retrieval window.")
        
        filled_count = 0
        for order in items:
            # Filter for actual fills (dealSize > 0)
            deal_size = float(order.get('dealSize', 0))
            if deal_size > 0:
                filled_count += 1
                side = order.get('side', 'unknown').upper()
                symbol = order.get('symbol', 'unknown')
                price = order.get('price', 'market')
                # Calculate actual executed price if market order
                if price == 0 or price == '0':
                     deal_funds = float(order.get('dealFunds', 0))
                     if deal_size > 0:
                         price = deal_funds / deal_size
                
                print(f"   - [FILLED] {order.get('createdAt', 0)}: {side} {symbol} | Size: {deal_size} | Price: {price}")
        
        if filled_count == 0:
            print("   ⚠️ No filled orders found in the recent history.")
            
    except Exception as e:
        print(f"   ❌ Error fetching history: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(verify_trades())
