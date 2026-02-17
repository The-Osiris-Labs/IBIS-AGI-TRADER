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
        return str(symbol or "").replace("-USDT", "").replace("-USDC", "")

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

            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
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
            default_friction = 0.0025  # 0.25% default

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
                conn.execute(
                    """
                INSERT INTO trades (symbol, side, order_id, quantity, price, fees, pnl, pnl_pct, reason)
                VALUES (?, 'SELL', ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        symbol,
                        order_id,
                        quantity,
                        exit_price,
                        entry_fee + exit_fee,
                        net_pnl,
                        pnl_pct,
                        reason,
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
