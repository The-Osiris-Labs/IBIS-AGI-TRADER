"""
IBIS v8 PROFESSIONAL DATABASE
SQLite-based state management with passive strategy support.
"""

import sqlite3
import datetime
import os
from datetime import date
from typing import Dict
from contextlib import contextmanager

DB_PATH = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v8.db"


class IbisDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_schema()

    def _ensure_db_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """Normalize symbol by stripping known quote currency suffixes (e.g., -USDT, -USDC)"""
        normalized = str(symbol or "").strip()
        # Only strip suffixes that are exactly at the end of the string
        if normalized.endswith("-USDT"):
            return normalized[:-5]
        if normalized.endswith("-USDC"):
            return normalized[:-5]
        return normalized

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def _init_schema(self):
        with self.get_conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                entry_fee REAL DEFAULT 0,
                current_price REAL,
                unrealized_pnl REAL,
                unrealized_pnl_pct REAL,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mode TEXT,
                stop_loss REAL,
                take_profit REAL,
                agi_score REAL,
                agi_insight TEXT,
                limit_sell_order_id TEXT,
                limit_sell_price REAL
            );

            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
                order_id TEXT,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                fees REAL DEFAULT 0,
                fee_rate REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pnl REAL,
                pnl_pct REAL,
                reason TEXT
            );

            CREATE TABLE IF NOT EXISTS fee_budget (
                date TEXT PRIMARY KEY,
                fees_used REAL DEFAULT 0,
                trades_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS fee_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
                order_id TEXT,
                fee_amount REAL NOT NULL,
                fee_rate REAL NOT NULL,
                trade_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
            CREATE INDEX IF NOT EXISTS idx_fee_history_symbol ON fee_history(symbol);
            CREATE INDEX IF NOT EXISTS idx_fee_history_timestamp ON fee_history(timestamp);
            """)

            # Add missing columns for existing databases
            for col, dtype in [
                ("entry_fee", "REAL DEFAULT 0"),
                ("limit_sell_order_id", "TEXT"),
                ("limit_sell_price", "REAL"),
            ]:
                try:
                    conn.execute(f"ALTER TABLE positions ADD COLUMN {col} {dtype}")
                except sqlite3.OperationalError:
                    pass  # Column already exists

            # Trades table migrations.
            try:
                conn.execute("ALTER TABLE trades ADD COLUMN order_id TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Create order-id dedup index after migrations.
            try:
                conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_trades_order_id_unique
                    ON trades(order_id)
                    WHERE order_id IS NOT NULL AND order_id != ''
                    """
                )
            except sqlite3.OperationalError:
                pass

    def update_position(
        self,
        symbol,
        quantity,
        price,
        stop_loss=None,
        take_profit=None,
        agi_score=None,
        agi_insight=None,
        entry_fee=None,
        limit_sell_order_id=None,
        limit_sell_price=None,
    ):
        symbol = self._normalize_symbol(symbol)
        with self.get_conn() as conn:
            conn.execute(
                """
            INSERT INTO positions (symbol, quantity, entry_price, entry_fee, current_price, stop_loss, take_profit, agi_score, agi_insight, limit_sell_order_id, limit_sell_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                quantity = excluded.quantity,
                entry_price = excluded.entry_price,
                entry_fee = COALESCE(excluded.entry_fee, positions.entry_fee),
                current_price = excluded.current_price,
                stop_loss = COALESCE(excluded.stop_loss, positions.stop_loss),
                take_profit = COALESCE(excluded.take_profit, positions.take_profit),
                agi_score = COALESCE(excluded.agi_score, positions.agi_score),
                agi_insight = COALESCE(excluded.agi_insight, positions.agi_insight),
                limit_sell_order_id = COALESCE(excluded.limit_sell_order_id, positions.limit_sell_order_id),
                limit_sell_price = COALESCE(excluded.limit_sell_price, positions.limit_sell_price)
            """,
                (
                    symbol,
                    quantity,
                    price,
                    entry_fee or 0,
                    price,
                    stop_loss,
                    take_profit,
                    agi_score,
                    agi_insight,
                    limit_sell_order_id,
                    limit_sell_price,
                ),
            )

        # Record entry fee in fee history
        if entry_fee and entry_fee > 0:
            trade_value = quantity * price
            fee_rate = entry_fee / trade_value if trade_value > 0 else 0

            # Validate fee rate is within reasonable bounds (0% to 5%)
            valid_fee_rate = max(0.0, min(0.05, fee_rate))

            with self.get_conn() as conn:
                conn.execute(
                    """
                INSERT INTO fee_history (symbol, side, order_id, fee_amount, fee_rate, trade_value)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (symbol, "BUY", limit_sell_order_id, entry_fee, valid_fee_rate, trade_value),
                )

    def set_state(self, key, value):
        with self.get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, str(value)),
            )

    def get_state(self, key, default=None):
        with self.get_conn() as conn:
            row = conn.execute("SELECT value FROM system_state WHERE key = ?", (key,)).fetchone()
            return row[0] if row else default

    def close_position(
        self,
        symbol,
        exit_price,
        reason="CLOSED",
        actual_fee=None,
        pnl=None,
        pnl_pct=None,
        order_id=None,
        fees=None,
    ):
        """Close a position and calculate net profit including fees.

        Args:
            symbol: The trading pair symbol
            exit_price: The exit price
            reason: Reason for closing
            actual_fee: Actual fee from KuCoin API (in USDT). If None, uses estimated friction.
        """
        try:
            from ..core.config import Config

            default_friction = Config.get_total_friction()
        except:
            default_friction = 0.00075  # 0.075% default (avg fee + slippage)

        symbol = self._normalize_symbol(symbol)
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT quantity, entry_price, entry_fee FROM positions WHERE symbol = ?",
                (symbol,),
            ).fetchone()
            if row:
                quantity = row["quantity"]
                entry_price = row["entry_price"]
                entry_fee = row["entry_fee"] if row and "entry_fee" in row else 0

                entry_val = quantity * entry_price
                exit_val = quantity * exit_price

                if fees is not None:
                    exit_fee = fees
                elif actual_fee is not None and actual_fee > 0:
                    exit_fee = actual_fee
                else:
                    exit_fee = exit_val * default_friction

                net_pnl = exit_val - entry_val - entry_fee - exit_fee if pnl is None else pnl
                if pnl_pct is None:
                    effective_friction = exit_fee / exit_val if exit_val > 0 else default_friction
                    friction = max(effective_friction, default_friction)
                    pnl_pct = (exit_price / entry_price - 1) - friction

                # Log trade with actual fees
                total_fees = entry_fee + exit_fee
                trade_value = quantity * exit_price
                fee_rate = total_fees / trade_value if trade_value > 0 else 0

                # Validate fee rate is within reasonable bounds (0% to 5%)
                valid_fee_rate = max(0.0, min(0.05, fee_rate))
                valid_exit_fee_rate = max(
                    0.0, min(0.05, exit_fee / trade_value if trade_value > 0 else 0)
                )

                conn.execute(
                    """
                INSERT INTO trades (symbol, side, order_id, quantity, price, fees, fee_rate, pnl, pnl_pct, reason)
                VALUES (?, 'SELL', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        symbol,
                        order_id,
                        quantity,
                        exit_price,
                        total_fees,
                        valid_fee_rate,
                        net_pnl,
                        pnl_pct,
                        reason,
                    ),
                )

                # Record detailed fee information
                conn.execute(
                    """
                INSERT INTO fee_history (symbol, side, order_id, fee_amount, fee_rate, trade_value)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        symbol,
                        "SELL",
                        order_id,
                        exit_fee,
                        valid_exit_fee_rate,
                        trade_value,
                    ),
                )

                # Close position
                conn.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))

    def get_open_positions(self):
        with self.get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM positions").fetchall()]

    def get_trades(self, limit=100):
        with self.get_conn() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,)
                ).fetchall()
            ]

    def record_fee(self, fee_amount: float):
        """Track daily fee usage"""
        from datetime import date

        today = date.today().isoformat()
        with self.get_conn() as conn:
            conn.execute(
                """
            INSERT INTO fee_budget (date, fees_used, trades_count)
            VALUES (?, ?, 1)
            ON CONFLICT(date) DO UPDATE SET
                fees_used = fee_budget.fees_used + ?,
                trades_count = fee_budget.trades_count + 1
            """,
                (today, fee_amount, fee_amount),
            )

    def get_fee_budget_status(self) -> Dict:
        """Get current daily fee budget status"""
        from datetime import date
        from ..core.trading_constants import TRADING

        today = date.today().isoformat()
        max_daily_fees = 100000 * TRADING.RISK.FEE_BUDGET_DAILY

        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT fees_used, trades_count FROM fee_budget WHERE date = ?",
                (today,),
            ).fetchone()

            fees_used = float(row["fees_used"]) if row else 0
            trades_count = int(row["trades_count"]) if row else 0

            return {
                "fees_used": fees_used,
                "max_allowed": max_daily_fees,
                "remaining": max_daily_fees - fees_used,
                "usage_pct": (fees_used / max_daily_fees * 100) if max_daily_fees > 0 else 0,
                "trades_today": trades_count,
                "budget_exceeded": fees_used > max_daily_fees,
            }

    def get_average_fees_per_symbol(self, days: int = 7) -> Dict[str, Dict[str, float]]:
        """Get average fees per symbol from historical trades and fee history for specific time period

        Args:
            days: Number of days to look back for fee history

        Returns:
            Dictionary of symbol -> {"maker": float, "taker": float, "count": int}
        """
        from datetime import datetime, timedelta
        import logging

        logger = logging.getLogger(__name__)

        if days <= 0:
            raise ValueError("Days must be a positive integer")

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        symbol_fees = {}

        with self.get_conn() as conn:
            # Check if we have data in fee_history table (preferred source) for last N days
            cursor = conn.execute(
                """
                SELECT symbol, 
                       AVG(fee_rate) as avg_fee_rate,
                       COUNT(*) as trade_count
                FROM fee_history 
                WHERE fee_rate > 0 AND fee_rate <= 1.0  -- Exclude invalid rates
                  AND timestamp >= ?
                GROUP BY symbol
            """,
                (cutoff_date,),
            )

            for row in cursor.fetchall():
                symbol = row["symbol"]
                avg_fee_rate = row["avg_fee_rate"]
                trade_count = row["trade_count"]

                # Clamp to realistic fee rate for major exchanges (0.01% to 0.1%)
                valid_fee_rate = max(0.0001, min(0.001, avg_fee_rate))
                if valid_fee_rate != avg_fee_rate:
                    logger.warning(
                        f"Invalid fee rate for {symbol}: {avg_fee_rate:.4f}, clamped to {valid_fee_rate:.4f}"
                    )

                symbol_fees[symbol] = {
                    "maker": valid_fee_rate,  # Assume symmetric fees for now
                    "taker": valid_fee_rate,
                    "count": trade_count,
                }

            # If no data in fee_history for last N days, check all time
            if not symbol_fees:
                cursor = conn.execute("""
                    SELECT symbol, 
                           AVG(fee_rate) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM fee_history 
                    WHERE fee_rate > 0 AND fee_rate <= 1.0  -- Exclude invalid rates
                    GROUP BY symbol
                """)

                for row in cursor.fetchall():
                    symbol = row["symbol"]
                    avg_fee_rate = row["avg_fee_rate"]
                    trade_count = row["trade_count"]

                    valid_fee_rate = max(0.0, min(0.05, avg_fee_rate))
                    if valid_fee_rate != avg_fee_rate:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {avg_fee_rate:.4f}, clamped to {valid_fee_rate:.4f}"
                        )

                    symbol_fees[symbol] = {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": trade_count,
                    }

            # If still no data, fall back to trades table for last N days
            if not symbol_fees:
                cursor = conn.execute(
                    """
                    SELECT symbol, 
                           AVG(fees / (quantity * price)) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM trades 
                    WHERE fees > 0 AND quantity > 0 AND price > 0
                      AND timestamp >= ?
                    GROUP BY symbol
                """,
                    (cutoff_date,),
                )

                for row in cursor.fetchall():
                    symbol = row["symbol"]
                    avg_fee_rate = row["avg_fee_rate"]
                    trade_count = row["trade_count"]

                    valid_fee_rate = max(0.0, min(0.05, avg_fee_rate))
                    if valid_fee_rate != avg_fee_rate:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {avg_fee_rate:.4f}, clamped to {valid_fee_rate:.4f}"
                        )

                    symbol_fees[symbol] = {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": trade_count,
                    }

            # Final fallback to all trades
            if not symbol_fees:
                cursor = conn.execute("""
                    SELECT symbol, 
                           AVG(fees / (quantity * price)) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM trades 
                    WHERE fees > 0 AND quantity > 0 AND price > 0
                    GROUP BY symbol
                """)

                for row in cursor.fetchall():
                    symbol = row["symbol"]
                    avg_fee_rate = row["avg_fee_rate"]
                    trade_count = row["trade_count"]

                    valid_fee_rate = max(0.0, min(0.05, avg_fee_rate))
                    if valid_fee_rate != avg_fee_rate:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {avg_fee_rate:.4f}, clamped to {valid_fee_rate:.4f}"
                        )

                    symbol_fees[symbol] = {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": trade_count,
                    }

            return symbol_fees

    def get_average_fee_rate(self, symbol: str = None, days: int = 7) -> Dict[str, float]:
        """Get average fee rate for a specific symbol or overall for specific time period

        Args:
            symbol: Optional symbol to get fee rate for
            days: Number of days to look back for fee history

        Returns:
            Dictionary with "maker", "taker", and "count" fields
        """
        from datetime import datetime, timedelta
        import logging

        logger = logging.getLogger(__name__)

        if days <= 0:
            raise ValueError("Days must be a positive integer")

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        if symbol:
            symbol = self._normalize_symbol(symbol)
            with self.get_conn() as conn:
                # Check fee_history table first for last N days
                cursor = conn.execute(
                    """
                    SELECT AVG(fee_rate) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM fee_history 
                    WHERE symbol = ? AND fee_rate > 0 AND fee_rate <= 1.0  -- Exclude invalid rates
                      AND timestamp >= ?
                """,
                    (symbol, cutoff_date),
                )

                row = cursor.fetchone()
                if row and row["avg_fee_rate"]:
                    # Clamp to reasonable fee rate (0% to 5%)
                    valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                    if valid_fee_rate != row["avg_fee_rate"]:
                        logger.warning(
                            f"Invalid fee rate for {symbol}: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                        )
                    return {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": row["trade_count"],
                    }

                # Check fee_history all time
                cursor = conn.execute(
                    """
                    SELECT AVG(fee_rate) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM fee_history 
                    WHERE symbol = ? AND fee_rate > 0 AND fee_rate <= 1.0
                """,
                    (symbol,),
                )

                row = cursor.fetchone()
                if row and row["avg_fee_rate"]:
                    valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                    if valid_fee_rate != row["avg_fee_rate"]:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                        )
                    return {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": row["trade_count"],
                    }

                # Fall back to trades table for last N days
                cursor = conn.execute(
                    """
                    SELECT AVG(fees / (quantity * price)) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM trades 
                    WHERE symbol = ? AND fees > 0 AND quantity > 0 AND price > 0
                      AND timestamp >= ?
                """,
                    (symbol, cutoff_date),
                )

                row = cursor.fetchone()
                if row and row["avg_fee_rate"]:
                    valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                    if valid_fee_rate != row["avg_fee_rate"]:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                        )
                    return {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": row["trade_count"],
                    }

                # Fall back to all trades
                cursor = conn.execute(
                    """
                    SELECT AVG(fees / (quantity * price)) as avg_fee_rate,
                           COUNT(*) as trade_count
                    FROM trades 
                    WHERE symbol = ? AND fees > 0 AND quantity > 0 AND price > 0
                """,
                    (symbol,),
                )

                row = cursor.fetchone()
                if row and row["avg_fee_rate"]:
                    valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                    if valid_fee_rate != row["avg_fee_rate"]:
                        logger.warning(
                            f"Warning: Invalid fee rate for {symbol}: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                        )
                    return {
                        "maker": valid_fee_rate,
                        "taker": valid_fee_rate,
                        "count": row["trade_count"],
                    }

        # Get overall average if symbol not specified or no data
        with self.get_conn() as conn:
            # Check fee_history table first for last N days
            cursor = conn.execute(
                """
                SELECT AVG(fee_rate) as avg_fee_rate,
                       COUNT(*) as trade_count
                FROM fee_history 
                WHERE fee_rate > 0 AND fee_rate <= 1.0  -- Exclude invalid rates
                  AND timestamp >= ?
            """,
                (cutoff_date,),
            )

            row = cursor.fetchone()
            if row and row["avg_fee_rate"]:
                valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                if valid_fee_rate != row["avg_fee_rate"]:
                    logger.warning(
                        f"Invalid overall fee rate: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                    )
                return {
                    "maker": valid_fee_rate,
                    "taker": valid_fee_rate,
                    "count": row["trade_count"],
                }

            # Check fee_history all time
            cursor = conn.execute("""
                SELECT AVG(fee_rate) as avg_fee_rate,
                       COUNT(*) as trade_count
                FROM fee_history 
                WHERE fee_rate > 0 AND fee_rate <= 1.0
            """)

            row = cursor.fetchone()
            if row and row["avg_fee_rate"]:
                valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                if valid_fee_rate != row["avg_fee_rate"]:
                    logger.warning(
                        f"Warning: Invalid overall fee rate: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                    )
                return {
                    "maker": valid_fee_rate,
                    "taker": valid_fee_rate,
                    "count": row["trade_count"],
                }

            # Fall back to trades table for last N days
            cursor = conn.execute(
                """
                SELECT AVG(fees / (quantity * price)) as avg_fee_rate,
                       COUNT(*) as trade_count
                FROM trades 
                WHERE fees > 0 AND quantity > 0 AND price > 0
                  AND timestamp >= ?
            """,
                (cutoff_date,),
            )

            row = cursor.fetchone()
            if row and row["avg_fee_rate"]:
                valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                if valid_fee_rate != row["avg_fee_rate"]:
                    logger.warning(
                        f"Warning: Invalid overall fee rate: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                    )
                return {
                    "maker": valid_fee_rate,
                    "taker": valid_fee_rate,
                    "count": row["trade_count"],
                }

            # Fall back to all trades
            cursor = conn.execute("""
                SELECT AVG(fees / (quantity * price)) as avg_fee_rate,
                       COUNT(*) as trade_count
                FROM trades 
                WHERE fees > 0 AND quantity > 0 AND price > 0
            """)

            row = cursor.fetchone()
            if row and row["avg_fee_rate"]:
                valid_fee_rate = max(0.0, min(0.05, row["avg_fee_rate"]))
                if valid_fee_rate != row["avg_fee_rate"]:
                    logger.warning(
                        f"Warning: Invalid overall fee rate: {row['avg_fee_rate']:.4f}, clamped to {valid_fee_rate:.4f}"
                    )
                return {
                    "maker": valid_fee_rate,
                    "taker": valid_fee_rate,
                    "count": row["trade_count"],
                }

        # Default fallback rates
        logger.debug("No fee history found, using default rates")
        return {
            "maker": 0.0010,  # 0.10%
            "taker": 0.0010,  # 0.10%
            "count": 0,
        }

    def fee_record_exists(self, order_id: str) -> bool:
        """Check if a fee record exists for a specific order ID"""
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM fee_history WHERE order_id = ?",
                (order_id,),
            ).fetchone()
            return row is not None

    def update_fee_tracking(
        self, symbol: str, fees: float, trade_value: float, side: str = None, order_id: str = None
    ):
        """Record detailed fee information for better analysis

        Args:
            symbol: Trading symbol
            fees: Fee amount in quote currency
            trade_value: Total trade value in quote currency
            side: Trade side (buy/sell)
            order_id: Unique order identifier

        Raises:
            ValueError: If input parameters are invalid
        """
        import logging

        logger = logging.getLogger(__name__)

        # Validate inputs
        if not symbol or len(symbol.strip()) == 0:
            raise ValueError("Symbol cannot be empty")
        if fees < 0:
            raise ValueError(f"Fees cannot be negative: {fees}")
        if trade_value <= 0:
            raise ValueError(f"Trade value must be positive: {trade_value}")
        if side and side not in ["BUY", "SELL", "UNKNOWN"]:
            raise ValueError(f"Invalid side: {side} - must be BUY, SELL, or UNKNOWN")

        # Check if record already exists to avoid duplicates
        if order_id and self.fee_record_exists(order_id):
            logger.debug(f"Fee record already exists for order: {order_id}")
            return

        symbol = self._normalize_symbol(symbol)
        fee_rate = fees / trade_value if trade_value > 0 else 0

        # Validate fee rate is within realistic bounds for major exchanges (0.01% to 0.1%)
        valid_fee_rate = max(0.0001, min(0.001, fee_rate))
        if valid_fee_rate != fee_rate:
            logger.warning(
                f"Fee rate {fee_rate:.4f} for {symbol} is outside valid range (0.01% to 0.1%), "
                f"clamped to {valid_fee_rate:.4f}"
            )

        try:
            with self.get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO fee_history (symbol, side, order_id, fee_amount, fee_rate, trade_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (symbol, side or "UNKNOWN", order_id, fees, valid_fee_rate, trade_value),
                )

            logger.debug(
                f"Fee record created: symbol={symbol}, side={side}, order_id={order_id}, "
                f"fee={fees:.4f}, rate={valid_fee_rate:.4f}"
            )

            # Also update the trades table if order_id is provided
            if order_id:
                with self.get_conn() as conn:
                    conn.execute(
                        """
                        UPDATE trades 
                        SET fees = ?, fee_rate = ?
                        WHERE order_id = ?
                    """,
                        (fees, valid_fee_rate, order_id),
                    )
                logger.debug(f"Updated trade fees for order: {order_id}")

        except Exception as e:
            logger.error(
                f"Failed to update fee tracking: symbol={symbol}, order_id={order_id} - {e}"
            )
            raise
