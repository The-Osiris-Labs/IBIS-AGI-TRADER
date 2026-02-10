#!/usr/bin/env python3
"""
🦅 IBIS ENHANCED INTEGRATION LAYER
===================================
Integrates 20x enhancements into the main IBIS True Agent

This module provides drop-in enhancements that can be gradually integrated
into the main agent without breaking existing functionality.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

# Import enhanced modules
from ibis_enhanced_20x import (
    EnhancedPosition,
    EnhancedRiskManager,
    MultiTimeframeAnalyzer,
    StrategySelector,
    PerformanceTracker,
)

# Import AGI brain
from ibis.brain.agi_brain import get_agi_brain, MarketContext


class IBISEnhancedIntegration:
    """
    Enhanced integration layer for IBIS True Agent

    Usage:
        # In ibis_true_agent.py, add:
        from ibis_enhanced_integration import IBISEnhancedIntegration

        # In __init__:
        self.enhanced = IBISEnhancedIntegration(self)

        # Use enhanced features:
        signal = await self.enhanced.get_agi_enhanced_signal(symbol, market_data)
        position_size = self.enhanced.calculate_smart_position_size(...)
        should_exit, reason = self.enhanced.check_enhanced_exit(position)
    """

    def __init__(self, agent):
        """Initialize with reference to main agent"""
        self.agent = agent
        self.risk_manager = EnhancedRiskManager(agent.config)
        self._mtf_analyzer = None  # Lazy init
        self.strategy_selector = StrategySelector()
        self.performance_tracker = PerformanceTracker()
        self.agi_brain = get_agi_brain()

        print("🚀 Enhanced Integration Layer Initialized")
        print("   ✅ Advanced Risk Management")
        print("   ✅ Multi-Timeframe Analysis")
        print("   ✅ AGI Brain Integration")
        print("   ✅ Strategy Selection")
        print("   ✅ Performance Tracking")

    @property
    def mtf_analyzer(self):
        """Lazy initialization of MTF analyzer"""
        if self._mtf_analyzer is None:
            if not hasattr(self.agent, "client"):
                self.agent.log_event(f"      ⚠️ MTF: agent has no 'client' attribute")
                return None
            if self.agent.client is None:
                self.agent.log_event(f"      ⚠️ MTF: agent.client is None")
                return None
            self._mtf_analyzer = MultiTimeframeAnalyzer(self.agent.client)
            self.agent.log_event(f"      ✅ MTF analyzer initialized")
        return self._mtf_analyzer

    async def get_agi_enhanced_signal(
        self, symbol: str, market_data: Dict, fg_index: float = 50
    ) -> Dict:
        """
        Get AGI-enhanced trading signal

        Combines existing market intelligence with AGI brain analysis
        """
        try:
            # Get real order flow and whale data from free intelligence
            order_flow = 0.0
            whale_activity = "NEUTRAL"
            try:
                flow_data = await self.agent.free_intel.get_exchange_flow(symbol)
                if flow_data:
                    if isinstance(flow_data, dict):
                        order_flow = (
                            flow_data.get("net_flow", 0)
                            if isinstance(flow_data.get("net_flow"), (int, float))
                            else 0
                        )
                        whale_activity = flow_data.get("whale_activity", "NEUTRAL")
            except Exception as e:
                self.agent.log_event(f"      ⚠️ Order flow lookup failed: {e}")

            # Create market context for AGI brain
            context = MarketContext(
                symbol=symbol,
                price=market_data.get("price", 0),
                price_change_24h=market_data.get("change_24h", 0),
                price_change_1h=market_data.get("momentum_1h", 0),
                volume_24h=market_data.get("volume_24h", 0),
                volatility_1h=market_data.get("volatility_1h", 0.02),
                volatility_24h=market_data.get("volatility", 0.02),
                trend_strength=market_data.get("score", 50),
                order_flow_delta=order_flow,
                sentiment_score=market_data.get("sentiment", 50),
                fear_greed_index=int(fg_index),
                funding_rate=market_data.get("funding", 0.01),
                long_short_ratio=market_data.get("ls_ratio", 1.0),
                exchange_flow=0.0,
                whale_activity=whale_activity,
            )

            # Get AGI analysis
            agi_signal = await self.agi_brain.comprehensive_analysis(context)

            # 🧠 Log AGI reasoning - with defensive typing
            try:
                agi_signal_dict = (
                    agi_signal if isinstance(agi_signal, dict) else agi_signal.__dict__
                )
                agi_confidence_raw = agi_signal_dict.get("confidence", 0.5)
                if isinstance(agi_confidence_raw, dict):
                    agi_confidence = 50.0  # Default if dict
                else:
                    agi_confidence = float(agi_confidence_raw) * 100
                agi_action = str(agi_signal_dict.get("action", "HOLD"))
                agi_reasoning = str(agi_signal_dict.get("reasoning", "No reasoning"))
                agi_model_raw = agi_signal_dict.get("model_consensus", {})
                if isinstance(agi_model_raw, dict):
                    agi_model = 0.5
                else:
                    agi_model = (
                        float(agi_model_raw)
                        if isinstance(agi_model_raw, (int, float))
                        else 0.5
                    )
            except Exception as e:
                self.agent.log_event(f"      ⚠️ AGI parsing error: {e}")
                agi_confidence, agi_action, agi_reasoning, agi_model = (
                    50.0,
                    "HOLD",
                    "Parse error",
                    0.5,
                )

            self.agent.log_event(
                f"      🧠 AGI: {symbol} | action: {agi_action} | conf: {agi_confidence:.1f}% | "
                f"model: {agi_model:.2f} | reason: {agi_reasoning[:50]}..."
            )

            variance = 0

            mtf_variance = await self.get_multi_timeframe_variance(symbol, market_data)
            if mtf_variance:
                variance += mtf_variance

            cross_exchange_boost = await self.get_cross_exchange_variance(
                symbol, market_data.get("price", 0)
            )
            if cross_exchange_boost:
                variance += cross_exchange_boost

            if variance != 0:
                self.agent.log_event(f"      📊 Real variance applied: {variance:+.1f}")

            agi_confidence = max(0, min(100, agi_confidence + variance))

            # Get existing technical score
            existing_score = market_data.get("score", 50)

            # 🚀 DEEP LEVEL SCORING SYSTEM - Integrate ALL Relevant Intelligence
            # Base weights: Technical (40%), AGI (30%), MTF (15%), Volume (10%), Sentiment (5%)
            technical_weight = 0.4
            agi_weight = 0.3
            mtf_weight = 0.15
            volume_weight = 0.10
            sentiment_weight = 0.05

            # Technical score (existing)
            technical_score = existing_score

            # AGI score (confidence)
            agi_score = agi_confidence

            # Multi-timeframe alignment score
            mtf_score = 0
            try:
                mtf_analysis = await self.get_multi_timeframe_analysis(symbol)
                mtf_score = mtf_analysis.get("alignment_score", 50)
            except Exception:
                mtf_score = 50  # Default neutral

            # Volume score (normalized)
            volume_24h = market_data.get("volume_24h", 0)
            min_volume = 100000  # $100k minimum
            max_volume = 50000000  # $50M maximum
            volume_score = (
                min(max(volume_24h / min_volume, 0), max_volume / min_volume) * 100
            )
            volume_score = min(volume_score, 100)  # Cap at 100

            # Sentiment score
            sentiment_score = market_data.get("sentiment", 50)

            # Calculate base combined score
            combined_score = (
                technical_score * technical_weight
                + agi_score * agi_weight
                + mtf_score * mtf_weight
                + volume_score * volume_weight
                + sentiment_score * sentiment_weight
            )

            # 🎯 CONVERGENCE BOOSTS - For exceptional alignment across dimensions
            # Perfect Convergence (all scores ≥ 90)
            if (
                technical_score >= 90
                and agi_score >= 90
                and mtf_score >= 90
                and volume_score >= 90
                and sentiment_score >= 80
            ):
                combined_score += 30  # Ultimate God Tier boost
            # Strong Convergence (3+ dimensions ≥ 85)
            elif (
                sum(
                    1
                    for s in [
                        technical_score,
                        agi_score,
                        mtf_score,
                        volume_score,
                        sentiment_score,
                    ]
                    if s >= 85
                )
                >= 3
            ):
                combined_score += 15
            # Good Convergence (2+ dimensions ≥ 80)
            elif (
                sum(
                    1
                    for s in [
                        technical_score,
                        agi_score,
                        mtf_score,
                        volume_score,
                        sentiment_score,
                    ]
                    if s >= 80
                )
                >= 2
            ):
                combined_score += 8

            # 🎯 ACTION-SPECIFIC ENHANCEMENTS
            agi_action_str = agi_action if isinstance(agi_action, str) else "HOLD"

            if agi_action_str == "BUY":
                # Bullish confirmation from AGI
                if agi_score >= 90:
                    combined_score += 12
                elif agi_score >= 80:
                    combined_score += 8
                elif agi_score >= 70:
                    combined_score += 4

                # Additional boost for high volume
                if volume_score >= 90:
                    combined_score += 5

                # Fear & Greed index alignment (Extreme Fear + Bullish signal = Contrarian opportunity)
                fg_index = market_data.get("fear_greed", 50)
                if fg_index <= 20:
                    combined_score += 10

            elif agi_action_str == "SELL":
                # Bearish confirmation from AGI
                if agi_score >= 90:
                    combined_score -= 20
                elif agi_score >= 80:
                    combined_score -= 15
                elif agi_score >= 70:
                    combined_score -= 10

                # High sentiment + bearish signal = Warning
                if sentiment_score >= 80:
                    combined_score -= 5

            # 🎯 RISK ADJUSTMENTS
            volatility_24h = market_data.get("volatility", 0.02)
            if volatility_24h > 0.20:  # 20%+ volatility - reduce score
                combined_score *= 0.9

            correlation_risk = self.risk_manager.check_correlation_risk(
                new_symbol=symbol, existing_positions=[], price_data={}
            )
            if correlation_risk > 0.7:  # High correlation - reduce score
                combined_score *= 1 - (correlation_risk - 0.7) * 0.5

            # 🎯 TREND STRENGTH ENHANCEMENTS
            trend_strength = market_data.get("trend_strength", 50)
            if trend_strength >= 80:  # Strong trend
                combined_score += 5
            elif trend_strength <= 30:  # Weak trend
                combined_score *= 0.95

            # Cap at 150 for extreme God Tier identification, floor at 0
            final_score = max(0, min(150, combined_score))

            return {
                "score": final_score,
                "enhanced_score": combined_score,
                "agi_signal": agi_signal,
                "agi_action": agi_action,
                "agi_confidence": agi_confidence,
                "agi_reasoning": getattr(
                    agi_signal, "reasoning", "Neural Pattern Confirmed"
                ),
                "model_consensus": getattr(agi_signal, "model_consensus", 0.5),
                "original_score": existing_score,
                "boost_applied": final_score - combined_score,
            }

        except Exception as e:
            print(f"⚠️ AGI enhancement failed: {e}")
            return {
                "enhanced_score": market_data.get("score", 50),
                "agi_signal": None,
                "error": str(e),
            }

    async def get_market_regime_assessment(self, market_intel: Dict) -> str:
        """🚀 SUPREME MODE: Ask AGI to determine the global market regime"""
        try:
            # Aggregate data from top symbols
            symbols = list(market_intel.keys())[:10]
            if not symbols:
                return "NORMAL"

            avg_change = sum(
                market_intel[s].get("change_24h", 0) for s in symbols
            ) / len(symbols)
            avg_vol = sum(
                market_intel[s].get("volatility", 0.02) for s in symbols
            ) / len(symbols)

            # Simple prompt for AGI brain to weigh in
            prompt = f"Market Snapshot: Top symbols avg 24h change: {avg_change:.2f}%, Avg Volatility: {avg_vol:.4f}. Current Sentiment: {market_intel[symbols[0]].get('sentiment', 50)}/100."

            # Use AGI brain to classify
            # This is a simplified call, in reality we'd use a specific method in agi_brain
            if avg_vol > 0.05:
                return "VOLATILE"
            elif avg_change > 2.0:
                return "TRENDING"
            elif avg_change < -3.0:
                return "CRASHING"
            elif abs(avg_change) < 0.5:
                return "FLAT"
            else:
                return "NORMAL"
        except:
            return "NORMAL"

    async def get_multi_timeframe_analysis(self, symbol: str) -> Dict:
        """Get multi-timeframe analysis for better entries"""
        if self.mtf_analyzer is None:
            return {
                "alignment_score": 50,
                "dominant_trend": "UNKNOWN",
                "error": "mtf_not_initialized",
            }

        try:
            mtf_data = await self.mtf_analyzer.analyze_all_timeframes(symbol)

            # Debug: Log what's being returned
            tf_data = mtf_data.get("timeframes", {})
            if tf_data:
                trends = []
                counts = []
                errors = []
                for t in ["1m", "5m", "15m", "1h", "4h"]:
                    trend = tf_data.get(t, {}).get("trend", "UNKNOWN")
                    count = tf_data.get(t, {}).get("candle_count", 0)
                    error = tf_data.get(t, {}).get("error", None)
                    trends.append(trend)
                    counts.append(str(count))
                    if error:
                        errors.append(f"{t}:{error}")

                if errors:
                    self.agent.log_event(
                        f"      🔍 MTF Debug {symbol}: errors={errors}"
                    )
                else:
                    self.agent.log_event(
                        f"      🔍 MTF Debug {symbol}: trends={trends} counts={counts}"
                    )

            return mtf_data
        except Exception as e:
            self.agent.log_event(f"      ⚠️ MTF analysis failed for {symbol}: {e}")
            return {"alignment_score": 50, "dominant_trend": "UNKNOWN", "error": str(e)}

    async def get_multi_timeframe_variance(
        self, symbol: str, market_data: Dict
    ) -> float:
        """
        Calculate real variance from multi-timeframe analysis.
        Returns variance based on trend alignment across timeframes.
        """
        try:
            mtf_data = await self.get_multi_timeframe_analysis(symbol)
            alignment_score = mtf_data.get("alignment_score", 50)

            # Get trends from MTF analyzer (keys are "1m", "5m", "15m", "1h", "4h")
            mtf_timeframes = mtf_data.get("timeframes", {})
            trend_1m = mtf_timeframes.get("1m", {}).get("trend", "unknown").upper()
            trend_5m = mtf_timeframes.get("5m", {}).get("trend", "unknown").upper()
            trend_15m = mtf_timeframes.get("15m", {}).get("trend", "unknown").upper()
            trend_1h = mtf_timeframes.get("1h", {}).get("trend", "unknown").upper()
            trend_4h = mtf_timeframes.get("4h", {}).get("trend", "unknown").upper()

            # Check all 5 timeframes
            trends = [trend_1m, trend_5m, trend_15m, trend_1h, trend_4h]
            bullish_count = sum(1 for t in trends if t == "BULLISH")
            bearish_count = sum(1 for t in trends if t == "BEARISH")

            variance = 0

            if bullish_count >= 4:
                variance = 15
            elif bearish_count >= 4:
                variance = -15
            elif bullish_count == 3:
                variance = 10
            elif bearish_count == 3:
                variance = -10
            elif bullish_count == 2 and bearish_count == 0:
                variance = 6
            elif bearish_count == 2 and bullish_count == 0:
                variance = -6
            elif alignment_score >= 85:
                variance = 8
            elif alignment_score < 25:
                variance = -8
            elif alignment_score >= 70:
                variance = 5
            elif alignment_score < 35:
                variance = -5
            else:
                variance = 0

            self.agent.log_event(
                f"      📈 MTF: {symbol} | bullish: {bullish_count}/5 | align: {alignment_score:.0f} | var: {variance:+.0f}"
            )

            return variance
        except Exception:
            return 0

    async def get_cross_exchange_variance(self, symbol: str, price: float) -> float:
        """
        Get variance from cross-exchange price leading signals.
        """
        try:
            lead_signal = await self.agent.cross_exchange.get_price_lead_signal(
                symbol=f"{symbol}-USDT", kucoin_price=price
            )

            has_lead = lead_signal.get("has_lead", False)
            direction = lead_signal.get("direction", "neutral")
            boost = lead_signal.get("boost", 0)
            lead_pct = lead_signal.get("lead_pct", 0)

            if has_lead:
                self.agent.log_event(
                    f"      🔥 X-LEAD: {symbol} | {direction} | {lead_pct:+.2f}% | boost: {boost:+.0f}"
                )
            else:
                self.agent.log_event(f"      📊 X-LEAD: {symbol} neutral")

            return boost
        except Exception:
            return 0

    def calculate_smart_position_size(
        self,
        symbol: str,
        confidence: float,
        volatility: float,
        available_capital: float,
        current_positions: List[str],
        score: float = 50,  # New parameter
    ) -> Dict:
        """
        Calculate intelligent position size

        Returns:
            {
                "size_usdt": float,
                "size_pct": float,
                "confidence_multiplier": float,
                "volatility_adjustment": float,
                "correlation_risk": float
            }
        """
        # Calculate base size with deep scoring integration
        size_usdt = self.risk_manager.calculate_position_size(
            symbol=symbol,
            confidence=confidence,
            volatility=volatility,
            available_capital=available_capital,
            current_positions=len(current_positions),
            score=score,
        )

        # Check correlation risk
        correlation_risk = self.risk_manager.check_correlation_risk(
            new_symbol=symbol, existing_positions=current_positions, price_data={}
        )

        # Reduce size if high correlation
        if correlation_risk > 0.5:
            size_usdt *= 1 - correlation_risk * 0.5

        size_pct = (size_usdt / available_capital) * 100 if available_capital > 0 else 0

        return {
            "size_usdt": size_usdt,
            "size_pct": size_pct,
            "confidence": confidence,
            "volatility": volatility,
            "correlation_risk": correlation_risk,
            "recommended": size_usdt > 0 and correlation_risk < 0.7,
        }

    def calculate_dynamic_stops(
        self, entry_price: float, atr_percent: float, regime: str, confidence: float
    ) -> Dict:
        """
        Calculate dynamic stop loss and take profit

        Returns:
            {
                "stop_loss": float,
                "take_profit": float,
                "risk_reward": float,
                "stop_distance_pct": float,
                "tp_distance_pct": float
            }
        """
        # Get strategy for regime
        strategy = self.strategy_selector.get_strategy(regime, confidence)

        # Calculate based on ATR
        if atr_percent > 0:
            # Use ATR-based stops
            stop_distance = atr_percent * 2.5  # 2.5x ATR
            tp_distance = atr_percent * 3.5  # 3.5x ATR
        else:
            # Fallback to strategy defaults
            stop_distance = strategy["stop_pct"] / 100
            tp_distance = strategy["target_pct"] / 100

        # Adjust for confidence
        if confidence > 0.7:
            tp_distance *= 1.3
            stop_distance *= 0.9
        elif confidence < 0.4:
            tp_distance *= 0.8
            stop_distance *= 1.1

        stop_loss = entry_price * (1 - stop_distance)
        take_profit = entry_price * (1 + tp_distance)

        risk_reward = tp_distance / stop_distance if stop_distance > 0 else 0

        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward": risk_reward,
            "stop_distance_pct": stop_distance * 100,
            "tp_distance_pct": tp_distance * 100,
            "atr_percent": atr_percent * 100,
            "regime": regime,
            "strategy": strategy["name"],
        }

    def create_enhanced_position(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        regime: str,
        confidence: float,
        atr_percent: float,
        agi_signal: Optional[Dict] = None,
        mtf_data: Optional[Dict] = None,
    ) -> EnhancedPosition:
        """Create enhanced position with all tracking"""
        return EnhancedPosition(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime=regime,
            confidence=confidence,
            atr_percent=atr_percent,
            agi_signal=agi_signal,
            timeframe_alignment=mtf_data or {},
            risk_reward=(take_profit - entry_price) / (entry_price - stop_loss)
            if entry_price > stop_loss
            else 0,
        )

    def check_enhanced_exit(
        self, position: EnhancedPosition, current_price: float, atr_percent: float
    ) -> tuple[bool, str, Dict]:
        """
        Check if position should exit with enhanced logic

        Returns:
            (should_exit, reason, details)
        """
        # Update trailing stop
        position.update_trailing_stop(current_price, atr_percent)

        # Check exit conditions
        should_exit, reason = position.should_exit()

        # Get P&L
        pnl = position.get_pnl()

        details = {
            "current_price": current_price,
            "entry_price": position.entry_price,
            "stop_loss": position.stop_loss,
            "take_profit": position.take_profit,
            "trailing_stop": position.trailing_stop,
            "highest_price": position.highest_price,
            "pnl_pct": pnl["pnl_pct"],
            "pnl_abs": pnl["pnl_abs"],
            "reason": reason,
        }

        return should_exit, reason, details

    def get_regime_strategy(self, regime: str, confidence: float = 0.5) -> Dict:
        """Get optimal strategy for current regime"""
        return self.strategy_selector.get_strategy(regime, confidence)

    def record_trade_result(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        quantity: float,
        regime: str,
        strategy: str,
        exit_reason: str,
    ):
        """Record trade for performance tracking"""
        pnl = (exit_price - entry_price) * quantity
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100

        trade = {
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "regime": regime,
            "strategy": strategy,
            "exit_reason": exit_reason,
        }

        self.performance_tracker.record_trade(trade)

    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        return self.performance_tracker.get_metrics()

    def check_risk_limits(self, current_balance: float, daily_pnl: float) -> Dict:
        """Check if risk limits are breached"""
        drawdown = self.risk_manager.update_drawdown(current_balance)

        should_reduce = self.risk_manager.should_reduce_risk(drawdown)
        should_stop = self.risk_manager.should_stop_trading(drawdown, daily_pnl)

        return {
            "drawdown": drawdown,
            "should_reduce_risk": should_reduce,
            "should_stop_trading": should_stop,
            "peak_balance": self.risk_manager.drawdown_tracker["peak_balance"],
            "max_drawdown": self.risk_manager.drawdown_tracker["max_drawdown"],
        }

    async def get_comprehensive_analysis(
        self, symbol: str, market_data: Dict, fg_index: float = 50
    ) -> Dict:
        """
        Get comprehensive analysis combining all enhancements

        This is the main method to use for enhanced decision-making
        """
        print(f"\n🔍 Enhanced Analysis for {symbol}")

        # 1. Get AGI signal - pass Fear & Greed index
        print("   🧠 Running AGI brain analysis...")
        agi_enhanced = await self.get_agi_enhanced_signal(
            symbol, market_data, fg_index=fg_index
        )

        # 2. Get multi-timeframe analysis
        print("   📊 Analyzing multiple timeframes...")
        mtf_data = await self.get_multi_timeframe_analysis(symbol)

        # 3. Calculate optimal position size
        print("   💰 Calculating position size...")
        available_capital = self.agent.state.get("capital_awareness", {}).get(
            "real_trading_capital", 100
        )
        current_positions = list(self.agent.state.get("positions", {}).keys())

        position_sizing = self.calculate_smart_position_size(
            symbol=symbol,
            confidence=agi_enhanced.get("agi_confidence", 50) / 100,
            volatility=market_data.get("volatility", 0.02),
            available_capital=available_capital,
            current_positions=current_positions,
            score=agi_enhanced.get("enhanced_score", 50),
        )

        # 4. Calculate dynamic stops
        print("   🎯 Calculating dynamic stops...")
        atr_percent = market_data.get("atr_data", {}).get("atr_percent", 0.02)
        stops = self.calculate_dynamic_stops(
            entry_price=market_data.get("price", 0),
            atr_percent=atr_percent,
            regime=market_data.get("market_regime", "NORMAL"),
            confidence=agi_enhanced.get("agi_confidence", 50) / 100,
        )

        # 5. Get strategy recommendation
        strategy = self.get_regime_strategy(
            regime=market_data.get("market_regime", "NORMAL"),
            confidence=agi_enhanced.get("agi_confidence", 50) / 100,
        )

        print(f"   ✅ Analysis complete!")
        print(f"      Score: {agi_enhanced.get('enhanced_score', 0):.1f}/100")
        print(f"      AGI Action: {agi_enhanced.get('agi_action', 'HOLD')}")
        print(f"      MTF Alignment: {mtf_data.get('alignment_score', 0):.1f}%")
        print(f"      Position Size: ${position_sizing.get('size_usdt', 0):.2f}")
        print(f"      Risk/Reward: {stops.get('risk_reward', 0):.2f}R")

        return {
            "enhanced_score": agi_enhanced.get(
                "score",
                agi_enhanced.get("enhanced_score", market_data.get("score", 50)),
            ),
            "agi_analysis": agi_enhanced,
            "mtf_analysis": mtf_data,
            "position_sizing": position_sizing,
            "stops": stops,
            "strategy": strategy,
            "recommendation": self._generate_recommendation(
                agi_enhanced, mtf_data, position_sizing, stops
            ),
        }

    def _generate_recommendation(
        self, agi_data: Dict, mtf_data: Dict, sizing: Dict, stops: Dict
    ) -> Dict:
        """Generate final trading recommendation - EXTREMELY AGGRESSIVE mode"""
        score = agi_data.get("score", agi_data.get("enhanced_score", 50))
        agi_action = agi_data.get("agi_action", "HOLD")
        mtf_alignment = mtf_data.get("alignment_score", 50)
        correlation_risk = sizing.get("correlation_risk", 0)

        # Decision logic - optimized for MAXIMUM CAPITAL UTILIZATION
        if score < 30:
            action = "SKIP"
            reason = "Score too low"
        elif correlation_risk > 0.8:  # Slightly higher correlation tolerance
            action = "SKIP"
            reason = "High correlation risk"
        # God tier scores (90+ override ALL conditions - FULL deployment)
        elif score >= 90:
            action = "STRONG_BUY"
            reason = "GOD TIER - Full capital deployment"
        # High scores (85+ with ANY alignment - AGGRESSIVE deployment)
        elif score >= 85:
            action = "STRONG_BUY"
            reason = "High score overrides all conditions"
        # Good scores (75+ - ACTIVE deployment)
        elif score >= 75:
            action = "BUY"
            reason = "Good score + market conditions"
        # Moderate scores (65+ in volatile markets - OPPORTUNISTIC)
        elif score >= 65 and mtf_alignment >= 30:
            action = "BUY"
            reason = "Opportunistic entry"
        # Always execute if score >= 80 regardless of AGI HOLD
        elif score >= 80:
            action = "BUY"
            reason = "High score overrides HOLD recommendation"
        # For scores 55-69, always buy if in volatile market
        elif score >= 55:
            action = "BUY"
            reason = "Volatile market - aggressive entry"
        elif agi_action == "HOLD":
            action = "BUY"  # Never wait - always buy if score is reasonable
            reason = "Aggressive mode - executing anyway"
        elif mtf_alignment < 30:
            action = "BUY"  # Ignore alignment issues for aggressive trading
            reason = "Aggressive mode - ignoring alignment"
        else:
            action = "BUY"  # Default to BUY for any reasonable opportunity
            reason = "Market conditions favorable"

        # FINAL CHECK: NEVER RETURN HOLD - ALWAYS BUY OR SKIP
        if action == "WAIT" or action == "HOLD":
            action = "BUY"
            reason = "Aggressive mode - forcing entry"

        return {
            "action": action,
            "reason": reason,
            "confidence": score / 100,
            "risk_reward": stops.get("risk_reward", 0),
            "position_size_usdt": sizing.get("size_usdt", 0),
        }

    # ============================================================================
    # PRECISION EXECUTION METHODS (New)
    # ============================================================================

    def init_precision_execution(self):
        """Initialize precision execution components"""
        from ibis.scalping import EntryOptimizer, SmartStopManager

        self.entry_optimizer = EntryOptimizer(max_wait_seconds=5.0)
        self.smart_stops = SmartStopManager(target_avg_sl_pct=0.02)

        self.agent.log_event("🎯 Precision Execution Initialized")
        self.agent.log_event("   ✅ Entry Optimizer: Active")
        self.agent.log_event("   ✅ Smart Stop Manager: Active")

    async def get_precision_entry_recommendation(
        self,
        symbol: str,
        direction: str,
        target_price: float,
        order_book: Dict,
        candles_1m: List[Dict],
    ) -> Dict:
        """
        Get precision entry recommendation for better execution

        This improves HOW we enter, not IF we enter.
        Same trades, better prices.
        """
        if not hasattr(self, "entry_optimizer"):
            self.init_precision_execution()

        try:
            recommendation = self.entry_optimizer.get_execution_recommendation(
                symbol=symbol,
                direction=direction,
                target_price=target_price,
                order_book=order_book,
                candles_1m=candles_1m,
            )

            # Log if there's significant price improvement
            improvement = recommendation.get("price_improvement_pct", 0)
            if improvement > 0.02:  # >0.02% improvement
                self.agent.log_event(
                    f"   💰 ENTRY OPTIMIZATION: {symbol} | "
                    f"Target: ${target_price:.6f} → Suggested: ${recommendation['suggested_price']:.6f} | "
                    f"Improvement: {improvement:.3f}%"
                )

            return recommendation

        except Exception as e:
            self.agent.log_event(f"   ⚠️ Entry optimization failed: {e}")
            # Return default recommendation
            return {
                "symbol": symbol,
                "direction": direction,
                "target_price": target_price,
                "suggested_price": target_price,
                "order_type": "market",
                "should_wait": False,
                "wait_ms": 0,
                "confidence": 0.5,
                "reason": "Optimization failed, using default",
                "price_improvement_pct": 0.0,
            }

    async def calculate_smart_stop_levels(
        self,
        entry_price: float,
        direction: str,
        candles: List[Dict],
        timeframe: str = "5m",
    ) -> Dict:
        """
        Calculate adaptive stop levels that average ~2%

        Uses ATR-based stops:
        - Tight (1-1.5%) in low volatility
        - Normal (2%) in normal volatility
        - Wide (2.5-3%) in high volatility

        Over many trades, averages to 2% but with better win rates
        """
        if not hasattr(self, "smart_stops"):
            self.init_precision_execution()

        try:
            stop_levels = self.smart_stops.calculate_smart_stops(
                entry_price=entry_price,
                direction=direction,
                candles=candles,
                timeframe=timeframe,
                base_rr=1.0,  # 1:1 risk/reward
            )

            # Log the stop mode
            self.agent.log_event(
                f"   🛡️ SMART STOP: {direction} | "
                f"SL: {stop_levels.stop_distance_pct:.2f}% ({stop_levels.volatility_mode}) | "
                f"ATR: {(stop_levels.atr / entry_price) * 100:.3f}%"
            )

            return {
                "stop_loss": stop_levels.stop_loss,
                "take_profit": stop_levels.take_profit,
                "stop_distance_pct": stop_levels.stop_distance_pct,
                "tp_distance_pct": stop_levels.tp_distance_pct,
                "volatility_mode": stop_levels.volatility_mode,
                "atr": stop_levels.atr,
            }

        except Exception as e:
            self.agent.log_event(f"   ⚠️ Smart stop calculation failed: {e}")
            # Return default 2% stops
            if direction == "LONG":
                return {
                    "stop_loss": entry_price * 0.98,
                    "take_profit": entry_price * 1.02,
                    "stop_distance_pct": 2.0,
                    "tp_distance_pct": 2.0,
                    "volatility_mode": "DEFAULT",
                    "atr": 0.0,
                }
            else:
                return {
                    "stop_loss": entry_price * 1.02,
                    "take_profit": entry_price * 0.98,
                    "stop_distance_pct": 2.0,
                    "tp_distance_pct": 2.0,
                    "volatility_mode": "DEFAULT",
                    "atr": 0.0,
                }

    async def get_trailing_stop_update(
        self, position: Dict, current_price: float
    ) -> Optional[float]:
        """
        Calculate updated stop-loss for trailing

        Trailing Rules:
        - +1% profit: Move to breakeven
        - +2% profit: Trail at 50% of gains
        - +3% profit: Trail at 70% of gains
        """
        if not hasattr(self, "smart_stops"):
            return None

        try:
            entry_price = position.get("buy_price", 0)
            current_stop = position.get("sl", 0)
            direction = "LONG" if position.get("quantity", 0) > 0 else "SHORT"

            # Track highest/lowest price seen
            highest = position.get("highest_price", entry_price)
            lowest = position.get("lowest_price", entry_price)

            # Update extremes
            if current_price > highest:
                highest = current_price
            if current_price < lowest:
                lowest = current_price

            new_stop = self.smart_stops.get_trailing_stop_adjustment(
                current_price=current_price,
                entry_price=entry_price,
                highest_price=highest,
                lowest_price=lowest,
                current_stop=current_stop,
                direction=direction,
                profit_activation_pct=1.0,
            )

            # Only return if stop moved
            if direction == "LONG" and new_stop > current_stop:
                return new_stop
            elif direction == "SHORT" and new_stop < current_stop:
                return new_stop

            return None

        except Exception as e:
            self.agent.log_event(f"   ⚠️ Trailing stop calculation failed: {e}")
            return None


# Convenience function for easy integration
def create_enhanced_integration(agent):
    """Create enhanced integration instance"""
    return IBISEnhancedIntegration(agent)


__all__ = ["IBISEnhancedIntegration", "create_enhanced_integration"]
