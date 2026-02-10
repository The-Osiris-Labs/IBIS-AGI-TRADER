#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - CHARTS 🦅                    ║
║                                                                      ║
║              Advanced Terminal Charts for Trading Analysis             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import random
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import plotext as plt

    PLOTEXT_AVAILABLE = True
except ImportError:
    PLOTEXT_AVAILABLE = False

from ibis.ui.colors import Colors


@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class ChartGenerator:
    """Generate various charts for trading analysis."""

    @staticmethod
    def generate_candles(count: int = 50, start_price: float = 100.0) -> List[Candle]:
        """Generate demo candlestick data."""
        candles = []
        price = start_price
        now = datetime.now()

        for i in range(count):
            timestamp = (now - timedelta(hours=count - i)).strftime("%H:%M")

            volatility = random.uniform(0.005, 0.02)
            change = random.gauss(0, volatility)

            open_price = price
            close_price = price * (1 + change)

            high_price = max(open_price, close_price) * (
                1 + random.uniform(0, volatility)
            )
            low_price = min(open_price, close_price) * (
                1 - random.uniform(0, volatility)
            )

            volume = random.uniform(1000, 10000)

            candles.append(
                Candle(
                    timestamp=timestamp,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                )
            )

            price = close_price

        return candles

    @staticmethod
    def candlestick_chart(
        candles: List[Candle],
        title: str = "Price Chart",
        width: int = 80,
        height: int = 20,
    ) -> str:
        """Generate ASCII candlestick chart."""
        if not candles:
            return "No data available"

        if PLOTEXT_AVAILABLE:
            plt.clf()
            plt.plotsize(width, height)

            dates = [c.timestamp for c in candles]
            opens = [c.open for c in candles]
            closes = [c.close for c in candles]
            highs = [c.high for c in candles]
            lows = [c.low for c in candles]

            plt.datetime_formatter(dates)
            plt.candlestick(dates, opens, closes, highs, lows, title=title)

            return plt.build()
        else:
            return ASCIICharts.candlestick(candles, title, width, height)

    @staticmethod
    def line_chart(
        data: List[float],
        title: str = "Trend",
        width: int = 80,
        height: int = 10,
    ) -> str:
        """Generate ASCII line chart."""
        if not data:
            return "No data"

        if PLOTEXT_AVAILABLE:
            plt.clf()
            plt.plotsize(width, height)
            plt.plot(data, title=title)
            return plt.build()
        else:
            return ASCIICharts.line(data, title, width, height)

    @staticmethod
    def multi_line_chart(
        data: Dict[str, List[float]],
        title: str = "Comparison",
        width: int = 80,
        height: int = 12,
    ) -> str:
        """Generate multi-line comparison chart."""
        if PLOTEXT_AVAILABLE:
            plt.clf()
            plt.plotsize(width, height)
            for label, values in data.items():
                plt.plot(values, label=label)
            plt.theme("dark")
            plt.title(title)
            return plt.build()
        else:
            return ASCIICharts.multi_line(data, title, width, height)

    @staticmethod
    def volume_bars(
        volumes: List[float],
        title: str = "Volume",
        width: int = 80,
        height: int = 8,
    ) -> str:
        """Generate ASCII volume bar chart."""
        if PLOTEXT_AVAILABLE:
            plt.clf()
            plt.plotsize(width, height)
            plt.bar(volumes, title=title)
            return plt.build()
        else:
            return ASCIICharts.volume(volumes, title, width, height)


class ASCIICharts:
    """Pure ASCII chart rendering without external dependencies."""

    @staticmethod
    def bar(
        data: Dict[str, float],
        title: str = "",
        width: int = 50,
        height: int = 10,
        colorize: bool = True,
    ) -> str:
        """Create a horizontal bar chart."""
        if not data:
            return ""

        max_val = max(data.values()) if data else 1
        max_key_len = max(len(str(k)) for k in data.keys()) if data else 10

        lines = []
        if title:
            lines.append(f"{Colors.BOLD}{title}{Colors.RESET}\n")

        for label, value in data.items():
            bar_len = int((value / max_val) * (width - max_key_len - 5))
            bar = "█" * bar_len + "░" * (width - max_key_len - 5 - bar_len)
            if colorize:
                color = Colors.GREEN if value >= 0 else Colors.RED
            else:
                color = Colors.RESET
            lines.append(
                f"{label:<{max_key_len}} │{color}{bar}{Colors.RESET} │ {value:+.2f}%"
            )

        return "\n".join(lines)

    @staticmethod
    def vertical_bar(
        data: List[float],
        labels: List[str] = None,
        title: str = "",
        width: int = 40,
        height: int = 10,
    ) -> str:
        """Create a vertical bar chart."""
        if not data:
            return ""

        max_val = max(data) if data else 1
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        lines = [f"{Colors.BOLD}{title}{Colors.RESET}\n"]

        for i in range(height - 1, -1, -1):
            line = ""
            for val in data:
                threshold = (i / height) * max_val
                if val >= threshold:
                    level = min(int((val / max_val) * len(chars)), len(chars) - 1)
                    line += chars[level] * 2
                else:
                    line += "  "
            lines.append(line)

        if labels:
            label_line = ""
            for _ in data:
                label_line += "‾‾"
            lines.append(label_line)
            label_row = ""
            for l in labels:
                label_row += f"{l[:2]} "
            lines.append(label_row)

        return "\n".join(lines)

    @staticmethod
    def gauge(
        value: float, title: str = "", width: int = 30, colorize: bool = True
    ) -> str:
        """Create a gauge meter."""
        pos = int(width * value)
        bar = "█" * pos + "░" * (width - pos)

        if colorize:
            if value >= 0.8:
                color = Colors.GREEN
            elif value >= 0.5:
                color = Colors.YELLOW
            else:
                color = Colors.RED
        else:
            color = Colors.RESET

        return f"{title}\n│{color}{bar}{Colors.RESET}│ {value:.0%}"

    @staticmethod
    def sparkline(data: List[float], width: int = 40, colorize: bool = True) -> str:
        """Create a sparkline chart."""
        if not data:
            return ""

        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1

        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        line = ""
        for val in data:
            normalized = (val - min_val) / range_val
            char_idx = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
            if colorize:
                color = Colors.GREEN if val >= data[0] else Colors.RED
            else:
                color = Colors.RESET
            line += f"{color}{chars[char_idx]}{Colors.RESET}"

        return line

    @staticmethod
    def pie_chart(data: Dict[str, float], title: str = "", size: int = 20) -> str:
        """Create a simple ASCII pie chart representation."""
        if not data:
            return ""

        total = sum(data.values()) if data else 1
        segments = []

        colors = [
            Colors.RED,
            Colors.GREEN,
            Colors.BLUE,
            Colors.YELLOW,
            Colors.MAGENTA,
            Colors.CYAN,
            Colors.BRIGHT_RED,
            Colors.BRIGHT_GREEN,
        ]

        for i, (label, value) in enumerate(data.items()):
            pct = value / total
            segments.append(
                {"label": label, "pct": pct, "color": colors[i % len(colors)]}
            )

        lines = [f"{Colors.BOLD}{title}{Colors.RESET}"]

        for seg in segments:
            bar_len = int(seg["pct"] * 20)
            bar = "█" * bar_len
            lines.append(
                f"{seg['color']}{bar}{Colors.RESET} {seg['label']}: {seg['pct'] * 100:.1f}%"
            )

        return "\n".join(lines)

    @staticmethod
    def heatmap_grid(
        data: List[List[float]],
        labels_x: List[str] = None,
        labels_y: List[str] = None,
        title: str = "",
    ) -> str:
        """Create a heatmap grid."""
        if not data:
            return ""

        chars = ["░", "▒", "▓", "█"]
        colors = [Colors.BLUE, Colors.CYAN, Colors.GREEN, Colors.YELLOW, Colors.RED]

        lines = [f"{Colors.BOLD}{title}{Colors.RESET}\n"]

        for y_idx, row in enumerate(data):
            line = ""
            if labels_y:
                line += (
                    f"{labels_y[y_idx]:<8} " if y_idx < len(labels_y) else "         "
                )

            for val in row:
                normalized = min(1.0, max(0.0, val))
                char_idx = int(normalized * (len(chars) - 1))
                color_idx = int(normalized * (len(colors) - 1))
                line += f"{colors[color_idx]}{chars[char_idx]}{Colors.RESET} "

            lines.append(line)

        if labels_x:
            x_line = "        "
            for _ in labels_x:
                x_line += "▔ "
            lines.append(x_line)
            x_labels = "        "
            for l in labels_x:
                x_labels += f"{l[:2]} "
            lines.append(x_labels)

        return "\n".join(lines)

    @staticmethod
    def candle(
        candles: List[Candle],
        title: str = "Candlestick Chart",
        width: int = 60,
        height: int = 15,
    ) -> str:
        """Draw a simplified candlestick chart."""
        if not candles or len(candles) < 2:
            return "Need at least 2 candles"

        closes = [
            float(c.get("close", 0) if isinstance(c, dict) else c.close)
            for c in candles
        ]
        highs = [
            float(c.get("high", 0) if isinstance(c, dict) else c.high) for c in candles
        ]
        lows = [
            float(c.get("low", 0) if isinstance(c, dict) else c.low) for c in candles
        ]

        min_price = min(lows[-30:]) if len(lows) >= 30 else min(lows)
        max_price = max(highs[-30:]) if len(highs) >= 30 else max(highs)
        price_range = max_price - min_price if max_price != min_price else 1

        lines = []
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")
        lines.append(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.WHITE}{title:^{width + 5}}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
        )
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")

        step = price_range / (height - 2)

        for i in range(height - 1, -1, -1):
            price_level = min_price + i * step
            line = f"{Colors.DIM}{price_level:>10.4f} {Colors.RESET}│"

            candle_data = candles[-width:] if len(candles) > width else candles

            for j, c in enumerate(candle_data):
                if isinstance(c, dict):
                    o, h, l, cl = (
                        float(c.get("open", 0)),
                        float(c.get("high", 0)),
                        float(c.get("low", 0)),
                        float(c.get("close", 0)),
                    )
                else:
                    o, h, l, cl = c.open, c.high, c.low, c.close

                if cl >= o:
                    color = Colors.GREEN
                    char = "▄" if abs(cl - o) < step * 0.5 else "█"
                else:
                    color = Colors.RED
                    char = "▄" if abs(cl - o) < step * 0.5 else "█"

                if l <= price_level <= h:
                    line += f"{color}│{Colors.RESET}"
                elif abs(cl - price_level) < step * 0.3:
                    line += f"{color}{char}{Colors.RESET}"
                else:
                    line += " "

            lines.append(line)

        lines.append(f"{Colors.DIM}{'─' * 12}└{'─' * width}{Colors.RESET}")
        lines.append(f"{Colors.DIM}{'':12} {datetime.now().strftime('%H:%M')}{'':^40}")

        return "\n".join(lines)

    @staticmethod
    def line(
        data: List[float],
        title: str = "Line Chart",
        width: int = 60,
        height: int = 10,
        colorize: bool = True,
    ) -> str:
        """Create a simple line chart."""
        if not data:
            return "No data"

        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1

        lines = []
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")
        lines.append(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.WHITE}{title:^{width + 5}}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
        )
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")

        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        for i in range(height - 1, -1, -1):
            threshold = min_val + (i / height) * range_val
            line = f"{Colors.DIM}{' ':12}{Colors.RESET}│"

            for val in data:
                normalized = (val - min_val) / range_val
                char_idx = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
                if colorize:
                    color = Colors.CYAN
                else:
                    color = Colors.RESET
                line += f"{color}{chars[char_idx]}{Colors.RESET}"

            lines.append(line)

        lines.append(f"{Colors.DIM}{'─' * 12}└{'─' * width}{Colors.RESET}")

        return "\n".join(lines)

    @staticmethod
    def multi_line(
        data: Dict[str, List[float]],
        title: str = "Multi-Line Chart",
        width: int = 60,
        height: int = 10,
    ) -> str:
        """Create a multi-line comparison chart."""
        lines = []
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")
        lines.append(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.WHITE}{title:^{width + 5}}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
        )
        lines.append(f"{Colors.BOLD}{'═' * (width + 15)}{Colors.RESET}")

        all_vals = []
        for values in data.values():
            all_vals.extend(values)

        min_val = min(all_vals) if all_vals else 0
        max_val = max(all_vals) if all_vals else 1
        range_val = max_val - min_val if max_val != min_val else 1

        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "█"]
        colors = [Colors.GREEN, Colors.CYAN, Colors.MAGENTA, Colors.YELLOW, Colors.RED]

        for i in range(height - 1, -1, -1):
            threshold = min_val + (i / height) * range_val
            line = f"{Colors.DIM}{' ':12}{Colors.RESET}│"

            for idx, values in enumerate(data.values()):
                if values:
                    val = values[-(i + 1)] if i < len(values) else 0
                    normalized = (val - min_val) / range_val
                    char_idx = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
                    color = colors[idx % len(colors)]
                    line += f"{color}{chars[char_idx]}{Colors.RESET}"
                else:
                    line += " "

            lines.append(line)

        lines.append(f"{Colors.DIM}{'─' * 12}└{'─' * width}{Colors.RESET}")

        legend = ""
        for idx, label in enumerate(data.keys()):
            color = colors[idx % len(colors)]
            legend += f"{color}{label[:4]}{Colors.RESET} "

        return "\n".join(lines) + f"\n{legend}"

    @staticmethod
    def volume(
        volumes: List[float],
        title: str = "Volume",
        width: int = 60,
        height: int = 8,
    ) -> str:
        """Create a volume bar chart."""
        if not volumes:
            return "No volume data"

        max_vol = max(volumes) if volumes else 1
        scale = height / max_vol if max_vol > 0 else 1

        lines = []
        lines.append(f"{Colors.BOLD}{'─' * (width + 15)}{Colors.RESET}")

        for i in range(height - 1, -1, -1):
            threshold = (i / height) * max_vol
            line = f"{Colors.DIM}{' ':12}{Colors.RESET}│"

            for vol in volumes[-width:]:
                bar_len = int(vol * scale)
                if bar_len >= height - i:
                    line += f"{Colors.CYAN}█{Colors.RESET}"
                else:
                    line += " "

            lines.append(line)

        lines.append(f"{Colors.DIM}{'─' * 12}└{'─' * width}{Colors.RESET}")

        return "\n".join(lines)


def demo_charts():
    """Demo the chart generation."""
    print("\n" + "=" * 80)
    print("  🦅 IBIS TRADING CHARTS DEMO")
    print("=" * 80 + "\n")

    candles = ChartGenerator.generate_candles(30, 100.0)

    print("📈 CANDLESTICK CHART (BTC-USDT)")
    print("-" * 80)
    print(ASCIICharts.candle(candles, "BTC-USDT 1H", 70, 15))
    print()

    print("📊 VOLUME BARS")
    print("-" * 80)
    volumes = [c.volume for c in candles]
    print(ASCIICharts.volume(volumes, "Volume", 70, 10))
    print()

    print("📉 PRICE HISTORY")
    print("-" * 80)
    closes = [c.close for c in candles]
    print(ASCIICharts.line(closes, "Price Trend", 70, 8))
    print()

    print("🔗 COMPARISON CHART")
    print("-" * 80)
    data = {
        "BTC": closes,
        "ETH": [c * random.uniform(0.03, 0.04) for c in closes],
        "SOL": [c * random.uniform(0.002, 0.003) for c in closes],
    }
    print(ASCIICharts.multi_line(data, "Crypto Comparison", 70, 12))
    print()


if __name__ == "__main__":
    demo_charts()
