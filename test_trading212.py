"""
Test script for Trading212 API integration
Run this to verify your Trading212 API key and portfolio access
"""
import asyncio
import sys
from src.brokers.trading212_client import Trading212Client
from config.settings import settings


async def test_trading212_connection():
    """Test Trading212 API connection and portfolio fetch"""

    print("=" * 60)
    print("Trading212 API Connection Test")
    print("=" * 60)

    # Check if API key is configured
    if not settings.trading212_api_key or settings.trading212_api_key == "your_trading212_api_key_here":
        print("\n❌ ERROR: Trading212 API key is not configured!")
        print("\nTo configure your API key:")
        print("1. Login to Trading212: https://www.trading212.com/")
        print("2. Go to Settings -> API (Beta)")
        print("3. Generate an API key")
        print("4. Copy the API key to your .env file as TRADING212_API_KEY")
        print("\nNote: Keep your API key secure and never share it!")
        return False

    print(f"\n✓ API Key configured: {settings.trading212_api_key[:8]}...")

    try:
        # Initialize client
        print("\n1. Initializing Trading212 client...")
        async with Trading212Client() as client:
            print("   ✓ Client initialized successfully")

            # Test account info
            print("\n2. Fetching account information...")
            try:
                account_info = await client.get_account_info()
                print(f"   ✓ Account ID: {account_info.get('id', 'N/A')}")
                print(f"   ✓ Currency: {account_info.get('currencyCode', 'N/A')}")
            except Exception as e:
                print(f"   ⚠ Could not fetch account info: {e}")

            # Test cash balance
            print("\n3. Fetching cash balance...")
            try:
                cash_info = await client.get_account_cash()
                print(f"   ✓ Free Cash: {cash_info.get('free', 0):.2f}")
                print(f"   ✓ Invested: {cash_info.get('invested', 0):.2f}")
                print(f"   ✓ Total: {cash_info.get('total', 0):.2f}")
                print(f"   ✓ P&L: {cash_info.get('ppl', 0):.2f}")
            except Exception as e:
                print(f"   ⚠ Could not fetch cash info: {e}")

            # Test portfolio fetch
            print("\n4. Fetching portfolio positions...")
            portfolio = await client.get_portfolio()

            if not portfolio:
                print("   ℹ No positions found in portfolio")
                return True

            print(f"   ✓ Found {len(portfolio)} position(s)\n")

            # Display positions
            print("-" * 80)
            print(f"{'Ticker':<15} {'Qty':<10} {'Avg Price':<12} {'Current':<12} {'P&L':<12}")
            print("-" * 80)

            total_value = 0
            total_pnl = 0

            for position in portfolio:
                ticker = position.get('ticker', 'N/A')
                quantity = position.get('quantity', 0)
                avg_price = position.get('averagePrice', 0)
                current_price = position.get('currentPrice', 0)
                ppl = position.get('ppl', 0)

                current_value = quantity * current_price
                total_value += current_value
                total_pnl += ppl

                print(f"{ticker:<15} {quantity:<10.2f} ${avg_price:<11.2f} ${current_price:<11.2f} ${ppl:<11.2f}")

            print("-" * 80)
            print(f"{'TOTAL':<15} {'':<10} {'':<12} ${total_value:<11.2f} ${total_pnl:<11.2f}")
            print("-" * 80)

            print("\n✅ SUCCESS: Trading212 integration is working correctly!")
            return True

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("  • Invalid API key")
        print("  • API key doesn't have required permissions")
        print("  • Network connectivity issues")
        print("  • Trading212 API service issues")
        return False


async def main():
    """Main test function"""
    success = await test_trading212_connection()

    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("  • Your Trading212 API is configured correctly")
        print("  • Start the API server: python main.py")
        print("  • Access portfolio at: http://localhost:8000/portfolio/trading212")
        print("  • View dashboard at: http://localhost:8000/")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Please fix the errors above and try again.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
