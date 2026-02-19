from ibis.core.logging_config import get_logger

"""
IBIS Position Rotation Manager
=============================
Continuous portfolio rotation system:
- Sells winners at TP
- Cuts losers at SL
- Consolidates dust positions
- Reallocates capital to new opportunities
- Keeps portfolio fresh and rotating

IMPORTANT: Reads positions from ibis_true_state.json (source of truth)
Writes closed trades to SQLite DB for analytics
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ibis.core.trading_constants import TRADING, SCORE_THRESHOLDS
from ibis.market_intelligence import market_intelligence
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.database.db import IbisDB
from ibis.data_consolidation import load_state, save_state

logger = get_logger(__name__)


@dataclass
class PositionEvaluation:
    """Evaluation result for a position"""

    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl_pct: float
    pnl_value: float
    age_hours: float
    score: float
    action: str  # HOLD, SELL_TP, SELL_SL, SELL_STALE, CONSOLIDATE
    reason: str
    sell_value: float


class PositionRotationManager:
    """
    Manages continuous portfolio rotation.

    Philosophy:
    - Winners are sold at TP to realize gains
    - Losers are cut at SL to limit damage
    - Stale positions (no movement) are rotated
    - Dust positions are consolidated
    - Capital is continuously reallocated
    """

    def __init__(self):
        self.client = get_kucoin_client()
        self.db = IbisDB()
        self.symbol_rules_cache: Dict[str, Dict] = {}

    async def _fetch_symbol_rules(self, symbol: str) -> Dict:
        """Fetch trading rules for a symbol"""
        if symbol in self.symbol_rules_cache:
            return self.symbol_rules_cache[symbol]

        try:
            rules = await self.client.get_symbol(symbol)
            if rules:
                self.symbol_rules_cache[symbol] = rules
                return rules
        except:
            pass
        return {}

    def _round_quantity(self, quantity: float, rules: Dict) -> float:
        """Round quantity to valid increments"""
        if rules:
            base_increment = float(rules.get("baseIncrement", 0.000001))
            if base_increment > 0:
                quantity = round(quantity / base_increment) * base_increment
        return float(f"{quantity:.8f}")

    async def evaluate_all_positions(self) -> List[PositionEvaluation]:
        """Evaluate all positions for potential action"""
        state = load_state()
        positions_dict = state.get("positions", {})
        evaluations = []

        for symbol, pos in positions_dict.items():
            currency = symbol
            symbol_usdt = f"{symbol}-USDT"

            try:
                ticker = await self.client.get_ticker(symbol_usdt)
                if not ticker:
                    continue

                current_price = float(ticker.price)
                entry_price = float(pos.get("buy_price", current_price))
                quantity = float(pos.get("quantity", 0))

                if entry_price <= 0:
                    entry_price = current_price

                # Calculate PnL
                pnl_pct = (current_price / entry_price - 1) * 100
                pnl_value = (current_price - entry_price) * quantity

                # Calculate age
                opened_at = pos.get("opened", datetime.now().isoformat())
                try:
                    opened = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
                    age_hours = (datetime.now() - opened).total_seconds() / 3600
                except:
                    age_hours = 24

                # Get AGI intelligence score from market intelligence
                try:
                    intel = await market_intelligence.get_combined_intelligence([currency])
                    score = market_intelligence.calculate_intelligence_score(currency, intel)
                except Exception as e:
                    score = max(0, min(100, 50 + pnl_pct * 5))

                # Determine action
                action, reason = self._determine_action(
                    pnl_pct=pnl_pct,
                    age_hours=age_hours,
                    quantity=quantity,
                    current_price=current_price,
                    score=score,
                    entry_price=entry_price,
                )

                sell_value = quantity * current_price

                eval_result = PositionEvaluation(
                    symbol=symbol_usdt,
                    quantity=quantity,
                    entry_price=entry_price,
                    current_price=current_price,
                    pnl_pct=pnl_pct,
                    pnl_value=pnl_value,
                    age_hours=age_hours,
                    score=score,
                    action=action,
                    reason=reason,
                    sell_value=sell_value,
                )
                evaluations.append(eval_result)

            except Exception as e:
                logger.warning(f"Error evaluating {symbol}: {e}")
                continue

        return evaluations

    def _determine_action(
        self,
        pnl_pct: float,
        age_hours: float,
        quantity: float,
        current_price: float,
        score: float,
        entry_price: float,
    ) -> Tuple[str, str]:
        """Determine what action to take with a position"""

        # Get TP/SL from position data (simplified)
        tp_pct = TRADING.RISK.TAKE_PROFIT_PCT * 100  # 1.5%
        sl_pct = TRADING.RISK.STOP_LOSS_PCT * 100  # 5.0%

        # 1. Take Profit - SELL
        if pnl_pct >= tp_pct:
            return "SELL_TP", f"Winner at +{pnl_pct:.2f}% (TP: {tp_pct}%)"

        # 2. Stop Loss - SELL
        if pnl_pct <= -sl_pct:
            return "SELL_SL", f"Loser at {pnl_pct:.2f}% (SL: -{sl_pct}%)"

        # 3. Stale Position (>48h with <1% movement) - SELL
        if age_hours > 48 and abs(pnl_pct) < 1:
            return "SELL_STALE", f"No movement in {age_hours:.0f}h"

        # 4. Very Old Position (>72h) - SELL for rotation
        if age_hours > 72:
            return "SELL_STALE", f"Stale position ({age_hours:.0f}h)"

        # 5. Poor AGI Score (<35) - SELL
        if score < 35:
            return "SELL_STALE", f"Low AGI score ({score:.0f})"

        # 6. Dust Position (<$1) - CONSOLIDATE
        position_value = quantity * current_price
        if position_value < 1.0:
            return "CONSOLIDATE", f"Dust position (${position_value:.4f})"

        # HOLD - Position is healthy
        return "HOLD", f"Healthy ({pnl_pct:+.2f}%, {age_hours:.0f}h)"

    async def execute_rotation(self) -> Dict:
        """
        Execute full rotation cycle.
        Returns summary of actions taken.
        """
        results = {
            "sold_tp": [],
            "sold_sl": [],
            "sold_stale": [],
            "consolidated": [],
            "total_realized_pnl": 0.0,
            "capital_freed": 0.0,
            "trades_executed": 0,
        }

        evaluations = await self.evaluate_all_positions()

        # Sort by action priority
        # First: Sell TP winners (we want to take profits)
        # Second: Sell SL losers (we want to cut losses)
        # Third: Sell stale/dust (we want to free capital)

        tp_evals = [e for e in evaluations if e.action == "SELL_TP"]
        sl_evals = [e for e in evaluations if e.action == "SELL_SL"]
        stale_evals = [e for e in evaluations if e.action == "SELL_STALE"]
        dust_evals = [e for e in evaluations if e.action == "CONSOLIDATE"]
        hold_evals = [e for e in evaluations if e.action == "HOLD"]

        # Execute sells in order
        for eval_result in tp_evals + sl_evals + stale_evals + dust_evals:
            success = await self._sell_position(eval_result)
            if success:
                results["trades_executed"] += 1
                results["total_realized_pnl"] += eval_result.pnl_value
                results["capital_freed"] += eval_result.sell_value

                if eval_result.action == "SELL_TP":
                    results["sold_tp"].append(eval_result.symbol)
                elif eval_result.action == "SELL_SL":
                    results["sold_sl"].append(eval_result.symbol)
                elif eval_result.action == "SELL_STALE":
                    results["sold_stale"].append(eval_result.symbol)
                elif eval_result.action == "CONSOLIDATE":
                    results["consolidated"].append(eval_result.symbol)

        # Log results
        logger.info(f"🔄 ROTATION COMPLETE: {results['trades_executed']} trades")
        if results["sold_tp"]:
            logger.info(f"   ✅ SOLD (TP): {', '.join(results['sold_tp'])}")
        if results["sold_sl"]:
            logger.info(f"   ❌ SOLD (SL): {', '.join(results['sold_sl'])}")
        if results["sold_stale"]:
            logger.info(f"   🔄 SOLD (STALE): {', '.join(results['sold_stale'])}")
        if results["consolidated"]:
            logger.info(f"   🧹 CONSOLIDATED: {', '.join(results['consolidated'])}")

        logger.info(
            f"   💰 PnL: ${results['total_realized_pnl']:+.4f} | Capital Freed: ${results['capital_freed']:.2f}"
        )

        return results

    async def _sell_position(self, eval_result: PositionEvaluation) -> bool:
        """Execute sell for a position with comprehensive TP/SL validation and order lifecycle management"""
        symbol = eval_result.symbol
        quantity = eval_result.quantity

        try:
            # Debug mode flag (can be enabled via environment variable or config)
            debug_mode = os.environ.get("IBIS_DEBUG", "false").lower() == "true"

            if debug_mode:
                logger.debug(
                    f"🔍 Debug: Entering _sell_position for {symbol} | Action: {eval_result.action} | Reason: {eval_result.reason} | Price: {eval_result.current_price:.6f} | Qty: {quantity:.8f}"
                )

            # Comprehensive validation: Ensure action is valid TP/SL type
            valid_actions = ["SELL_TP", "SELL_SL"]
            if eval_result.action not in valid_actions:
                logger.error(
                    f"❌ Invalid sell action for {symbol}: {eval_result.action} (must be one of {', '.join(valid_actions)})"
                )
                return False

            currency = symbol.replace("-USDT", "")
            balances = await self.client.get_all_balances(min_value_usd=0)
            actual_balance = float(balances.get(currency, {}).get("balance", 0))

            if actual_balance <= 0:
                logger.info(f"⚠️ Position {symbol} already closed (balance: {actual_balance})")
                self.db.close_position(symbol, eval_result.current_price, "ALREADY_CLOSED")
                if debug_mode:
                    logger.debug(
                        f"🔍 Debug: Position {symbol} already closed, balance: {actual_balance}"
                    )
                return False

            # Get position details from database
            position = None
            positions = self.db.get_open_positions()
            for pos in positions:
                if pos.get("symbol") == symbol:
                    position = pos
                    break

            limit_sell_price = position.get("limit_sell_price") if position else None
            limit_sell_order_id = position.get("limit_sell_order_id") if position else None

            rules = await self._fetch_symbol_rules(symbol)
            sell_qty = self._round_quantity(actual_balance, rules)

            if sell_qty <= 0:
                logger.warning(f"⚠️ Invalid quantity for {symbol}: {sell_qty}")
                if debug_mode:
                    logger.debug(f"🔍 Debug: Invalid quantity {sell_qty} for {symbol}")
                return False

            logger.info(f"🛑 SELLING: {symbol} | Qty: {sell_qty:.8f} | {eval_result.reason}")

            # Determine if we should use existing limit order or create new order
            if limit_sell_price and limit_sell_order_id:
                logger.info(
                    f"   📝 Found existing limit sell order: {limit_sell_order_id} @ ${limit_sell_price:.6f}"
                )

                # Check if current price matches or exceeds TP (for take profit)
                if eval_result.action == "SELL_TP":
                    if eval_result.current_price >= limit_sell_price:
                        logger.info(f"   🎯 Take profit reached - using existing limit order")
                        # Check if limit order is still active
                        try:
                            order = await self.client.get_order(limit_sell_order_id, symbol)
                            if order and order.status == "ACTIVE":
                                logger.info(f"   ✅ Limit order still active - waiting for fill")
                                if debug_mode:
                                    logger.debug(
                                        f"🔍 Debug: Order {limit_sell_order_id} is active, waiting for fill"
                                    )
                                return False  # Order is active, let it fill
                            elif order and order.status == "DONE":
                                logger.info(f"   ✅ Limit order already filled")
                                self.db.close_position(symbol, limit_sell_price, eval_result.action)
                                if debug_mode:
                                    logger.debug(
                                        f"🔍 Debug: Order {limit_sell_order_id} already filled, position closed"
                                    )
                                return True
                            else:
                                logger.warning(
                                    f"   ⚠️ Limit order {limit_sell_order_id} has unexpected status: {order.status if order else 'None'}"
                                )
                                if debug_mode:
                                    logger.debug(
                                        f"🔍 Debug: Order {limit_sell_order_id} has unexpected status: {order.status if order else 'None'}"
                                    )
                        except Exception as e:
                            logger.warning(f"   ⚠️ Could not check limit order status: {e}")
                            if debug_mode:
                                logger.debug(f"🔍 Debug: Failed to check order status: {e}")
                    else:
                        logger.warning(
                            f"   ⚠️ Take profit not actually reached - current price ({eval_result.current_price:.6f}) < TP ({limit_sell_price:.6f})"
                        )
                        if debug_mode:
                            logger.debug(
                                f"🔍 Debug: TP validation failed - current price {eval_result.current_price:.6f} < TP {limit_sell_price:.6f}"
                            )
                        return False

                # For stop loss, cancel existing limit order and create market order
                if eval_result.action == "SELL_SL":
                    # Validate stop loss price
                    entry_price = position.get("entry_price", eval_result.current_price)
                    stop_loss_price = entry_price * (1 - TRADING.RISK.STOP_LOSS_PCT)
                    if eval_result.current_price > stop_loss_price:
                        logger.warning(
                            f"   ⚠️ Stop loss not actually reached - current price ({eval_result.current_price:.6f}) > SL ({stop_loss_price:.6f})"
                        )
                        if debug_mode:
                            logger.debug(
                                f"🔍 Debug: SL validation failed - current price {eval_result.current_price:.6f} > SL {stop_loss_price:.6f}"
                            )
                        return False

                    logger.info(
                        f"   🛑 {eval_result.action} - canceling limit order and placing market sell"
                    )
                    try:
                        await self.client.cancel_order(limit_sell_order_id)
                        logger.info(f"   ✅ Limit order canceled")
                        if debug_mode:
                            logger.debug(
                                f"🔍 Debug: Successfully canceled order {limit_sell_order_id}"
                            )
                    except Exception as e:
                        logger.warning(f"   ⚠️ Could not cancel limit order: {e}")
                        if debug_mode:
                            logger.debug(
                                f"🔍 Debug: Failed to cancel order {limit_sell_order_id}: {e}"
                            )

            # If no valid limit order or we canceled it, create market order
            order = await self.client.create_market_order(symbol, "sell", sell_qty)

            # Close in DB
            self.db.close_position(symbol, eval_result.current_price, eval_result.action)
            logger.info(
                f"✅ SOLD: {symbol} | PnL: {eval_result.pnl_pct:+.2f}% | Order: {order.order_id}"
            )
            if debug_mode:
                logger.debug(
                    f"🔍 Debug: Market sell order executed successfully - Order ID: {order.order_id}"
                )

            return True

        except Exception as e:
            logger.error(f"❌ SELL FAILED {symbol}: {e}", exc_info=True)
            if debug_mode:
                logger.debug(f"🔍 Debug: Exception in _sell_position: {e}", exc_info=True)
            return False

    async def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary from state JSON"""
        state = load_state()
        positions_dict = state.get("positions", {})

        total_value = 0
        total_pnl = 0
        winners = 0
        losers = 0

        position_details = []

        for symbol, pos in positions_dict.items():
            symbol_usdt = f"{symbol}-USDT"
            entry_price = float(pos.get("buy_price", 0))
            quantity = float(pos.get("quantity", 0))

            try:
                ticker = await self.client.get_ticker(symbol_usdt)
                if ticker:
                    current_price = float(ticker.price)
                    value = quantity * current_price
                    pnl = (current_price - entry_price) * quantity
                    pnl_pct = (current_price / entry_price - 1) * 100 if entry_price > 0 else 0

                    total_value += value
                    total_pnl += pnl

                    if pnl > 0:
                        winners += 1
                    else:
                        losers += 1

                    position_details.append(
                        {
                            "symbol": symbol_usdt,
                            "quantity": quantity,
                            "entry_price": entry_price,
                            "current_price": current_price,
                            "value": value,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct,
                        }
                    )
            except:
                continue

        balances = await self.client.get_all_balances()
        usdt = float(balances.get("USDT", {}).get("available", 0))

        return {
            "positions_count": len(positions_dict),
            "winners": winners,
            "losers": losers,
            "total_value": total_value,
            "total_pnl": total_pnl,
            "available_usdt": usdt,
            "total_portfolio_value": total_value + usdt,
            "positions": sorted(position_details, key=lambda x: x["pnl"], reverse=True),
        }


async def run_rotation_cycle():
    """Run a single rotation cycle"""
    manager = PositionRotationManager()
    results = await manager.execute_rotation()
    summary = await manager.get_portfolio_summary()
    return results, summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results, summary = asyncio.run(run_rotation_cycle())
    print("\n📊 PORTFOLIO SUMMARY")
    print(f"Positions: {summary['positions_count']}")
    print(f"Winners: {summary['winners']} | Losers: {summary['losers']}")
    print(f"Total Value: ${summary['total_value']:.2f}")
    print(f"Total PnL: ${summary['total_pnl']:+.4f}")
    print(f"Available USDT: ${summary['available_usdt']:.2f}")
