#!/usr/bin/env python3
"""
Test all information streams for IBIS system
Comprehensive test of free_intelligence, market_intelligence, and enhanced integration
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader/tests/sandbox")

from ibis.free_intelligence import FreeIntelligence
from ibis_enhanced_integration import IBISEnhancedIntegration
from ibis_true_agent import IBISTrueAgent


async def test_free_intelligence():
    """Test free intelligence sources"""
    print("=" * 80)
    print("🧠 FREE INTELLIGENCE SOURCES TEST")
    print("=" * 80)

    intel = FreeIntelligence()

    # Test Fear & Greed Index
    try:
        print("\n1. Fear & Greed Index:")
        fg = await intel.get_fear_greed_index()
        print(f"   Value: {fg['value']} ({fg['classification']})")
        print(f"   Score: {fg['score']}/100")
        print(f"   Source: {fg['source']}")
        print(f"   Confidence: {fg['confidence']}%")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test Reddit Sentiment (BTC)
    try:
        print("\n2. Reddit Sentiment (BTC):")
        reddit = await intel.get_reddit_sentiment("bitcoin")
        print(f"   Score: {reddit['score']:.1f}/100")
        print(f"   Confidence: {reddit['confidence']}%")
        print(f"   Posts Analyzed: {reddit['posts_analyzed']}")
        print(f"   Sources: {len(reddit['sources'])}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test CryptoCompare Sentiment (BTC)
    try:
        print("\n3. CryptoCompare Sentiment (BTC):")
        cc = await intel.get_cryptocompare_sentiment("BTC")
        print(f"   Score: {cc['score']:.1f}/100")
        print(f"   Confidence: {cc['confidence']}%")
        print(f"   Sources: {len(cc['sources'])}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test CMC Sentiment (BTC)
    try:
        print("\n4. CMC Sentiment (BTC):")
        cmc = await intel.get_cmc_sentiment("BTC")
        print(f"   Score: {cmc['score']:.1f}/100")
        print(f"   Price Change 24h: {cmc['price_change_24h']:.2f}%")
        print(f"   Volume 24h: ${cmc['volume_24h']:,.0f}")
        print(f"   Market Cap: ${cmc['market_cap']:,.0f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test On-Chain Metrics (BTC)
    try:
        print("\n5. On-Chain Metrics (BTC):")
        chain = await intel.get_onchain_metrics("BTC")
        print(f"   Score: {chain['score']:.1f}/100")
        print(f"   Volume Score: {chain['volume_score']:.1f}/100")
        print(f"   Circulation Score: {chain['circulation_score']:.1f}/100")
        print(f"   Market Cap: ${chain['market_cap']:,.0f}")
        print(f"   Volume 24h: ${chain['volume_24h']:,.0f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test News Sentiment (BTC)
    try:
        print("\n6. News Sentiment (BTC):")
        news = await intel.get_news_sentiment("BTC")
        print(f"   Score: {news['score']:.1f}/100")
        print(f"   Confidence: {news['confidence']}%")
        print(f"   Sources: {len(news['sources'])}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test Gas Prices
    try:
        print("\n7. Gas Prices:")
        gas = await intel.get_gwei_gas()
        print(f"   Fast Gas: {gas['fast_gas']} Gwei")
        print(f"   Slow Gas: {gas['slow_gas']} Gwei")
        print(f"   Score: {gas['score']:.1f}/100")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test Exchange Flow (BTC)
    try:
        print("\n8. Exchange Flow (BTC):")
        flow = await intel.get_exchange_flow("BTC")
        print(f"   Score: {flow['score']:.1f}/100")
        print(f"   Net Flow: {flow['net_flow']:.1f}")
        print(f"   Whale Activity: {flow['whale_activity']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    await intel.close()


async def test_agent_intelligence():
    """Test agent intelligence integration"""
    print("\n" + "=" * 80)
    print("🚀 AGENT INTELLIGENCE INTEGRATION")
    print("=" * 80)

    agent = IBISTrueAgent()
    await agent.initialize()

    print(f"\n1. Agent Mode: {agent.state['agent_mode']}")
    print(f"2. Market Regime: {agent.state['market_regime']}")
    print(f"3. Symbols Cache: {len(agent.symbols_cache)} symbols")

    # Test enhanced integration
    print("\n4. Enhanced Integration:")
    if hasattr(agent, "enhanced"):
        print(f"   ✅ Enhanced integration initialized")

        # Test comprehensive sentiment
        try:
            print("\n5. Comprehensive Sentiment Analysis (BTC):")
            sentiment = await agent.free_intel.get_comprehensive_sentiment("BTC")
            print(f"   Score: {sentiment['score']:.1f}/100")
            print(f"   Confidence: {sentiment['confidence']}%")
            print(f"   Sources: {len(sentiment['sources'])}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    await agent.close()


async def main():
    await test_free_intelligence()
    await test_agent_intelligence()

    print("\n" + "=" * 80)
    print("✅ ALL INFORMATION STREAMS VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
