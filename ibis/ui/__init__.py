#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - UNIFIED UI 🦅               ║
║                                                                      ║
║              Complete Terminal Interface for Trading                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Unified exports for all UI components.
"""

from .colors import Colors, ColorGradients
from .icons import Icons
from .components import (
    IBISDashboard,
    Spinner,
    ProgressBar,
    ScanAnimator,
    format_number,
    format_duration,
    format_pnl,
    format_score,
    format_decision,
)
from .charts import (
    ChartGenerator,
    Candle,
    ASCIICharts,
)
from .animations import LoadingAnimation, ProgressAnimator

try:
    from .dashboards.textual_enhanced import IBISEnhancedApp

    TEXTUAL_AVAILABLE = True
except (ImportError, NameError):
    TEXTUAL_AVAILABLE = False
    IBISEnhancedApp = None

__all__ = [
    "Colors",
    "ColorGradients",
    "Icons",
    "IBISDashboard",
    "Spinner",
    "ProgressBar",
    "ScanAnimator",
    "format_number",
    "format_duration",
    "format_pnl",
    "format_score",
    "format_decision",
    "ChartGenerator",
    "Candle",
    "ASCIICharts",
    "IBISEnhancedApp",
    "LoadingAnimation",
    "ProgressAnimator",
    "TEXTUAL_AVAILABLE",
]

VERSION = "5.5.0"
