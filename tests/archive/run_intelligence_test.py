#!/usr/bin/env python3
import asyncio
import logging
from ibis_true_agent import IBISAutonomousAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ibis_test.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


async def run_test():
    try:
        logger.info("🚀 Initializing IBIS True Agent for intelligence test")

        agent = IBISAutonomousAgent()

        logger.info("🔗 Connecting to exchange...")
        await agent.initialize()

        logger.info("📊 Starting symbol discovery...")
        await agent.discover_market()
        logger.info(f"📊 Found {len(agent.symbols_cache)} trading pairs")

        logger.info("📋 Fetching symbol rules...")
        await agent.fetch_symbol_rules()
        logger.info(f"📋 Loaded rules for {len(agent.symbol_rules)} symbols")

        logger.info("🧠 Analyzing market intelligence...")
        market_intel = await agent.analyze_market_intelligence()
        logger.info(f"🧠 Analyzed {len(market_intel)} high-quality opportunities")

        if market_intel:
            # Check first few opportunities
            for i, (symbol, data) in enumerate(list(market_intel.items())[:5]):
                logger.info(f"🎯 Opportunity {i + 1}: {symbol}")
                logger.info(f"   Score: {data['score']:.1f}/100")
                logger.info(f"   Price: ${data['price']:.4f}")
                logger.info(f"   Risk Level: {data.get('risk_level', 'MEDIUM')}")
                logger.info(f"   Type: {data.get('opportunity_type', 'UNCERTAIN')}")
                logger.info(f"   Insights: {data.get('insights', [])}")

                if "liquidity_score" in data:
                    logger.info(f"   Liquidity: {data['liquidity_score']}")
                if "technical_strength" in data:
                    logger.info(f"   Technical Strength: {data['technical_strength']}")

                logger.info("-" * 50)

        logger.info("✅ Test completed successfully")

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback

        logger.error(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
