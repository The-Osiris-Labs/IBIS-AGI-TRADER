"""
IBIS Data Storage
Persistent storage for trades, positions, and system state.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterable
from dataclasses import dataclass
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "ibis_unified.db"


@dataclass
class TradeRecord:
    """Trade record for storage."""

    symbol: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_pct: float
    entry_reason: str = ""
    exit_reason: str = ""
    entry_time: str = ""
    exit_time: str = ""
    duration_minutes: float = 0.0
    confidence: float = 0.0
    status: str = ""
    fees: float = 0.0
    slippage: float = 0.0


@dataclass
class PositionRecord:
    """Position record for storage."""

    symbol: str
    side: str
    entry_price: float
    size: float
    current_price: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    opened_at: str = ""
    updated_at: str = ""


@dataclass
class MarketSnapshot:
    """Market data snapshot."""

    symbol: str
    price: float
    change_24h: float
    volume: float
    regime: str = ""
    trend: str = ""
    volatility: float = 0.0
    captured_at: str = ""


class DataStorage:
    """
    Data Storage - Persistent storage for trading data.

    Features:
    - SQLite database
    - Trade history
    - Position tracking
    - Market snapshots
    - Performance analytics
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize database."""
        try:
            print("Initializing Data Storage...")

            # Create tables
            self._create_tables()

            self.initialized = True
            print("✓ Data Storage ready!")
            return True

        except Exception as e:
            print(f"❌ Data Storage init failed: {e}")
            return False

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self) -> None:
        """Create database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    size REAL NOT NULL,
                    pnl REAL,
                    pnl_pct REAL,
                    entry_reason TEXT,
                    exit_reason TEXT,
                    entry_time TEXT,
                    exit_time TEXT,
                    duration_minutes REAL,
                    confidence REAL,
                    status TEXT,
                    fees REAL DEFAULT 0,
                    slippage REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._ensure_trades_schema(cursor)

            # Positions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    size REAL NOT NULL,
                    current_price REAL DEFAULT 0,
                    pnl REAL DEFAULT 0,
                    pnl_pct REAL DEFAULT 0,
                    stop_loss REAL,
                    take_profit REAL,
                    opened_at TEXT,
                    updated_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _ensure_trades_schema(self, cursor: sqlite3.Cursor) -> None:
        """Ensure trades table has expected columns (lightweight migration)."""
        cursor.execute("PRAGMA table_info(trades)")
        cols = {row[1] for row in cursor.fetchall()}
        if "duration_minutes" not in cols:
            cursor.execute("ALTER TABLE trades ADD COLUMN duration_minutes REAL")

            # Market snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL,
                    volume REAL,
                    regime TEXT,
                    trend TEXT,
                    volatility REAL,
                    captured_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _normalize_trade(self, trade: Any) -> TradeRecord:
        """Normalize various trade shapes into TradeRecord."""
        if isinstance(trade, TradeRecord):
            return trade

        # Dict-like input
        if isinstance(trade, dict):
            return TradeRecord(
                symbol=trade.get("symbol", ""),
                side=str(trade.get("side", trade.get("action", "buy"))).lower(),
                entry_price=float(trade.get("entry_price", trade.get("price", 0.0)) or 0.0),
                exit_price=float(trade.get("exit_price", 0.0) or 0.0),
                size=float(trade.get("size", trade.get("quantity", 0.0)) or 0.0),
                pnl=float(trade.get("pnl", 0.0) or 0.0),
                pnl_pct=float(trade.get("pnl_pct", 0.0) or 0.0),
                entry_reason=trade.get("entry_reason", "") or trade.get("reason", "") or "",
                exit_reason=trade.get("exit_reason", "") or "",
                entry_time=str(trade.get("entry_time", trade.get("timestamp", "")) or ""),
                exit_time=str(trade.get("exit_time", "") or ""),
                duration_minutes=float(trade.get("duration_minutes", 0.0) or 0.0),
                confidence=float(trade.get("confidence", 0.0) or 0.0),
                status=str(trade.get("status", "")),
                fees=float(trade.get("fees", trade.get("fee", 0.0)) or 0.0),
                slippage=float(trade.get("slippage", trade.get("slippage_pct", 0.0)) or 0.0),
            )

        # Object-like input (UnifiedTradingEngine.Trade)
        side = getattr(trade, "side", None) or getattr(trade, "action", "buy")
        reasons = getattr(trade, "reasons", []) or []
        entry_reason = reasons[0] if isinstance(reasons, list) and reasons else ""
        timestamp = getattr(trade, "timestamp", "") or ""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        return TradeRecord(
            symbol=getattr(trade, "symbol", ""),
            side=str(side).lower(),
            entry_price=float(getattr(trade, "entry_price", getattr(trade, "price", 0.0)) or 0.0),
            exit_price=float(getattr(trade, "exit_price", 0.0) or 0.0),
            size=float(getattr(trade, "size", getattr(trade, "quantity", 0.0)) or 0.0),
            pnl=float(getattr(trade, "pnl", 0.0) or 0.0),
            pnl_pct=float(getattr(trade, "pnl_pct", 0.0) or 0.0),
            entry_reason=entry_reason,
            exit_reason=str(getattr(trade, "exit_reason", "") or ""),
            entry_time=str(getattr(trade, "entry_time", timestamp) or ""),
            exit_time=str(getattr(trade, "exit_time", "") or ""),
            duration_minutes=float(getattr(trade, "duration_minutes", 0.0) or 0.0),
            confidence=float(getattr(trade, "confidence", 0.0) or 0.0),
            status=str(getattr(trade, "status", "") or ""),
            fees=float(getattr(trade, "fees", getattr(trade, "fee", 0.0)) or 0.0),
            slippage=float(getattr(trade, "slippage", getattr(trade, "slippage_pct", 0.0)) or 0.0),
        )

    def _normalize_position(self, position: Any) -> PositionRecord:
        """Normalize various position shapes into PositionRecord."""
        if isinstance(position, PositionRecord):
            return position

        if isinstance(position, dict):
            opened_at = position.get("opened_at", "") or position.get("entry_time", "")
            updated_at = position.get("updated_at", "") or position.get("last_update", "")
            return PositionRecord(
                symbol=position.get("symbol", ""),
                side=str(position.get("side", position.get("action", "buy"))).lower(),
                entry_price=float(position.get("entry_price", 0.0) or 0.0),
                size=float(position.get("size", position.get("quantity", 0.0)) or 0.0),
                current_price=float(position.get("current_price", 0.0) or 0.0),
                pnl=float(position.get("pnl", 0.0) or 0.0),
                pnl_pct=float(position.get("pnl_pct", 0.0) or 0.0),
                stop_loss=float(position.get("stop_loss", 0.0) or 0.0),
                take_profit=float(position.get("take_profit", 0.0) or 0.0),
                opened_at=str(opened_at or ""),
                updated_at=str(updated_at or ""),
            )

        opened_at = getattr(position, "opened_at", None) or getattr(position, "entry_time", "")
        updated_at = getattr(position, "updated_at", None) or getattr(position, "last_update", "")
        if isinstance(opened_at, datetime):
            opened_at = opened_at.isoformat()
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        return PositionRecord(
            symbol=getattr(position, "symbol", ""),
            side=str(getattr(position, "side", getattr(position, "action", "buy"))).lower(),
            entry_price=float(getattr(position, "entry_price", 0.0) or 0.0),
            size=float(getattr(position, "size", getattr(position, "quantity", 0.0)) or 0.0),
            current_price=float(getattr(position, "current_price", 0.0) or 0.0),
            pnl=float(getattr(position, "pnl", 0.0) or 0.0),
            pnl_pct=float(getattr(position, "pnl_pct", 0.0) or 0.0),
            stop_loss=float(getattr(position, "stop_loss", 0.0) or 0.0),
            take_profit=float(getattr(position, "take_profit", 0.0) or 0.0),
            opened_at=str(opened_at or ""),
            updated_at=str(updated_at or ""),
        )

    # ========== Trade Operations ==========

    async def save_trade(self, trade: Any) -> int:
        """Save a trade to database."""
        trade = self._normalize_trade(trade)
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO trades (
                    symbol, side, entry_price, exit_price, size, pnl, pnl_pct,
                    entry_reason, exit_reason, entry_time, exit_time,
                    duration_minutes, confidence, status, fees, slippage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    trade.symbol,
                    trade.side,
                    trade.entry_price,
                    trade.exit_price,
                    trade.size,
                    trade.pnl,
                    trade.pnl_pct,
                    trade.entry_reason,
                    trade.exit_reason,
                    trade.entry_time,
                    trade.exit_time,
                    trade.duration_minutes,
                    trade.confidence,
                    trade.status,
                    trade.fees,
                    trade.slippage,
                ),
            )

            trade_id = cursor.lastrowid
            conn.commit()

            return trade_id

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """Get trades from database."""
        query = "SELECT * FROM trades"
        params = []

        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            columns = [desc[0] for desc in cursor.description]
            trades = []

            for row in cursor.fetchall():
                trades.append(dict(zip(columns, row)))

            return trades

    async def get_trade_stats(self) -> Dict:
        """Get trade statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total trades
            cursor.execute("SELECT COUNT(*) FROM trades")
            total_trades = cursor.fetchone()[0]

            if total_trades == 0:
                return {
                    "total_trades": 0,
                    "win_rate": 0,
                    "total_pnl": 0,
                    "avg_win": 0,
                    "avg_loss": 0,
                    "profit_factor": 0,
                }

            # Winning trades
            cursor.execute("SELECT COUNT(*) FROM trades WHERE pnl > 0")
            wins = cursor.fetchone()[0]

            # P&L totals
            cursor.execute("SELECT SUM(pnl) FROM trades WHERE pnl > 0")
            total_win = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(pnl) FROM trades WHERE pnl <= 0")
            total_loss = abs(cursor.fetchone()[0] or 0)

            # Average win/loss
            cursor.execute("SELECT AVG(pnl) FROM trades WHERE pnl > 0")
            avg_win = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(pnl) FROM trades WHERE pnl <= 0")
            avg_loss = cursor.fetchone()[0] or 0

            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            profit_factor = total_win / total_loss if total_loss > 0 else float("inf")

            return {
                "total_trades": total_trades,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_win - total_loss, 4),
                "avg_win": round(avg_win, 4),
                "avg_loss": round(avg_loss, 4),
                "profit_factor": round(profit_factor, 2),
            }

    # ========== Position Operations ==========

    async def save_position(self, position: Any) -> int:
        """Save or update position."""
        position = self._normalize_position(position)
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if position exists
            cursor.execute(
                "SELECT id FROM positions WHERE symbol = ?", (position.symbol,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update
                cursor.execute(
                    """
                    UPDATE positions SET
                        current_price = ?,
                        pnl = ?,
                        pnl_pct = ?,
                        updated_at = ?
                    WHERE symbol = ?
                """,
                    (
                        position.current_price,
                        position.pnl,
                        position.pnl_pct,
                        datetime.now().isoformat(),
                        position.symbol,
                    ),
                )
                return existing[0]
            else:
                # Insert
                cursor.execute(
                    """
                    INSERT INTO positions (
                        symbol, side, entry_price, size, current_price, pnl, pnl_pct,
                        stop_loss, take_profit, opened_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        position.symbol,
                        position.side,
                        position.entry_price,
                        position.size,
                        position.current_price,
                        position.pnl,
                        position.pnl_pct,
                        position.stop_loss,
                        position.take_profit,
                        position.opened_at,
                        position.updated_at,
                    ),
                )
                return cursor.lastrowid

    async def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM positions ORDER BY opened_at DESC")

            columns = [desc[0] for desc in cursor.description]
            positions = []

            for row in cursor.fetchall():
                positions.append(dict(zip(columns, row)))

            return positions

    async def close_position(self, symbol: str) -> bool:
        """Remove a position from database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
            return cursor.rowcount > 0

    # ========== Market Snapshot Operations ==========

    async def save_market_snapshot(self, snapshot: MarketSnapshot) -> int:
        """Save market snapshot."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO market_snapshots (
                    symbol, price, change_24h, volume, regime, trend, volatility, captured_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.symbol,
                    snapshot.price,
                    snapshot.change_24h,
                    snapshot.volume,
                    snapshot.regime,
                    snapshot.trend,
                    snapshot.volatility,
                    snapshot.captured_at,
                ),
            )

            return cursor.lastrowid

    async def get_market_history(
        self,
        symbol: str,
        limit: int = 100,
    ) -> List[Dict]:
        """Get market history for symbol."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM market_snapshots
                WHERE symbol = ?
                ORDER BY captured_at DESC
                LIMIT ?
            """,
                (symbol, limit),
            )

            columns = [desc[0] for desc in cursor.description]
            snapshots = []

            for row in cursor.fetchall():
                snapshots.append(dict(zip(columns, row)))

            return snapshots

    # ========== Settings Operations ==========

    async def save_setting(self, key: str, value: str) -> None:
        """Save a setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """,
                (key, value, datetime.now().isoformat()),
            )

            conn.commit()

    async def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))

            result = cursor.fetchone()
            return result[0] if result else default

    # ========== Chat History ==========

    async def save_chat_message(
        self,
        sender: str,
        message: str,
        response: str = "",
    ) -> int:
        """Save chat message."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO chat_history (sender, message, response, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (sender, message, response, datetime.now().isoformat()),
            )

            return cursor.lastrowid

    async def get_chat_history(self, limit: int = 100) -> List[Dict]:
        """Get chat history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            columns = [desc[0] for desc in cursor.description]
            messages = []

            for row in cursor.fetchall():
                messages.append(dict(zip(columns, row)))

            return messages

    # ========== Backup/Restore ==========

    async def backup(self, backup_path: str) -> bool:
        """Create database backup."""
        try:
            import shutil

            shutil.copy(self.db_path, backup_path)
            return True
        except Exception:
            return False

    async def restore(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            import shutil

            shutil.copy(backup_path, self.db_path)
            return True
        except Exception:
            return False

    async def shutdown(self) -> None:
        """Shutdown storage."""
        self.initialized = False
        print("Data Storage shutdown complete")


def get_storage(db_path: Optional[str] = None) -> DataStorage:
    """Get storage instance."""
    return DataStorage(db_path)
