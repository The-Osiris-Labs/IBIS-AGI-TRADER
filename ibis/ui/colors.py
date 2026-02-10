#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - COLOR SYSTEM 🦅            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

class Colors:
    """Extended terminal color palette for maximum visual impact."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    INVERSE = "\033[7m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BRIGHT_BG_BLACK = "\033[100m"
    BRIGHT_BG_RED = "\033[101m"
    BRIGHT_BG_GREEN = "\033[102m"
    BRIGHT_BG_YELLOW = "\033[103m"
    BRIGHT_BG_BLUE = "\033[104m"
    BRIGHT_BG_MAGENTA = "\033[105m"
    BRIGHT_BG_CYAN = "\033[106m"
    BRIGHT_BG_WHITE = "\033[107m"

    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Generate RGB color code."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Generate RGB background color code."""
        return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def hex(hex_color: str) -> str:
        """Convert hex color to ANSI RGB."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return Colors.rgb(r, g, b)

    @staticmethod
    def gradient(start: str, end: str, steps: int) -> list:
        """Generate gradient between two hex colors."""
        start = start.lstrip("#")
        end = end.lstrip("#")

        r1, g1, b1 = int(start[0:2], 16), int(start[2:4], 16), int(start[4:6], 16)
        r2, g2, b2 = int(end[0:2], 16), int(end[2:4], 16), int(end[4:6], 16)

        colors = []
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / (steps - 1))
            g = int(g1 + (g2 - g1) * i / (steps - 1))
            b = int(b1 + (b2 - b1) * i / (steps - 1))
            colors.append(Colors.rgb(r, g, b))

        return colors


class ColorGradients:
    """Pre-defined color gradients for charts and displays."""

    GREEN_GRADIENT = [
        "\033[38;2;0;100;0m",
        "\033[38;2;0;140;0m",
        "\033[38;2;0;180;0m",
        "\033[38;2;50;200;50m",
        "\033[38;2;100;255;100m",
    ]

    RED_GRADIENT = [
        "\033[38;2;100;0;0m",
        "\033[38;2;140;0;0m",
        "\033[38;2;180;0;0m",
        "\033[38;2;200;50;50m",
        "\033[38;2;255;100;100m",
    ]

    GOLD_GRADIENT = [
        "\033[38;2;139;69;19m",
        "\033[38;2;184;134;11m",
        "\033[38;2;218;165;32m",
        "\033[38;2;255;215;0m",
        "\033[38;2;255;255;100m",
    ]

    BLUE_GRADIENT = [
        "\033[38;2;0;0;100m",
        "\033[38;2;0;0;140m",
        "\033[38;2;0;0;180m",
        "\033[38;2;50;50;200m",
        "\033[38;2;100;100;255m",
    ]

    PURPLE_GRADIENT = [
        "\033[38;2;75;0;130m",
        "\033[38;2;100;0;180m",
        "\033[38;2;128;0;128m",
        "\033[38;2;180;50;180m",
        "\033[38;2;220;100;220m",
    ]

    HEATMAP_COLORS = [
        "\033[48;2;0;0;255m",
        "\033[48;2;0;128;255m",
        "\033[48;2;0;255;255m",
        "\033[48;2;0;255;128m",
        "\033[48;2;0;255;0m",
        "\033[48;2;255;255;0m",
        "\033[48;2;255;128;0m",
        "\033[48;2;255;0;0m",
    ]

    @staticmethod
    def get_chart_color(value: float, inverse: bool = False) -> str:
        """Get color based on value (0-1)."""
        if inverse:
            return ColorGradients.RED_GRADIENT[int(value * 4)]
        return ColorGradients.GREEN_GRADIENT[int(value * 4)]

    @staticmethod
    def get_heatmap_color(value: float) -> str:
        """Get heatmap color for value (0-1)."""
        idx = int(value * (len(ColorGradients.HEATMAP_COLORS) - 1))
        return ColorGradients.HEATMAP_COLORS[idx]


class TradeColors:
    """Color scheme for trading displays."""

    BUY = Colors.BRIGHT_GREEN
    SELL = Colors.BRIGHT_RED
    STRONG_BUY = Colors.GREEN
    STRONG_SELL = Colors.RED
    NEUTRAL = Colors.YELLOW
    POSITIVE = Colors.CYAN
    NEGATIVE = Colors.MAGENTA

    POSITION_LONG = Colors.BRIGHT_GREEN
    POSITION_SHORT = Colors.BRIGHT_RED
    POSITION_NONE = Colors.DIM

    UP = Colors.GREEN
    DOWN = Colors.RED
    UNCHANGED = Colors.YELLOW

    RISK_LOW = Colors.BRIGHT_GREEN
    RISK_MEDIUM = Colors.YELLOW
    RISK_HIGH = Colors.BRIGHT_RED

    ALERT_HIGH = Colors.BRIGHT_RED
    ALERT_MEDIUM = Colors.YELLOW
    ALERT_LOW = Colors.CYAN

    TABLE_HEADER = Colors.BRIGHT_CYAN
    TABLE_ROW_ALT = Colors.DIM

    CHART_UP = Colors.GREEN
    CHART_DOWN = Colors.RED
    CHART_NEUTRAL = Colors.YELLOW
    CHART_VOLUME = Colors.CYAN


class ThemeManager:
    """Manage color themes for the terminal interface."""

    THEMES = {
        "dark": {
            "background": Colors.BLACK,
            "foreground": Colors.WHITE,
            "primary": Colors.CYAN,
            "secondary": Colors.MAGENTA,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
            "info": Colors.BLUE,
        },
        "light": {
            "background": Colors.WHITE,
            "foreground": Colors.BLACK,
            "primary": Colors.BLUE,
            "secondary": Colors.MAGENTA,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
            "info": Colors.CYAN,
        },
        "terminal": {
            "background": Colors.BLACK,
            "foreground": Colors.BRIGHT_GREEN,
            "primary": Colors.BRIGHT_GREEN,
            "secondary": Colors.BRIGHT_CYAN,
            "success": Colors.BRIGHT_GREEN,
            "warning": Colors.BRIGHT_YELLOW,
            "error": Colors.BRIGHT_RED,
            "info": Colors.BRIGHT_BLUE,
        },
    }

    def __init__(self, theme: str = "dark"):
        self.current_theme = theme
        self.themes = self.THEMES

    def set_theme(self, theme: str):
        """Change the active theme."""
        if theme in self.themes:
            self.current_theme = theme

    @property
    def colors(self):
        """Get current theme colors."""
        return self.themes[self.current_theme]

    def apply_theme(self):
        """Apply current theme to terminal."""
        colors = self.colors
        return f"{colors['background']}{colors['foreground']}"


def gradient_text(text: str, colors_list: list) -> str:
    """Apply gradient colors to text character by character."""
    if not colors_list or not text:
        return text

    result = ""
    colors_count = len(colors_list)
    text_len = len(text)

    for i, char in enumerate(text):
        color_idx = int(i / text_len * (colors_count - 1))
        result += f"{colors_list[color_idx]}{char}"

    return result + Colors.RESET


def rainbow_text(text: str) -> str:
    """Apply rainbow colors to text."""
    rainbow = [
        Colors.RED,
        Colors.YELLOW,
        Colors.GREEN,
        Colors.CYAN,
        Colors.BLUE,
        Colors.MAGENTA,
    ]
    return gradient_text(text, rainbow)


if __name__ == "__main__":
    print("🦅 IBIS Color System Demo")
    print("=" * 50)

    print("\nBasic Colors:")
    for name in ["RED", "GREEN", "YELLOW", "BLUE", "CYAN", "MAGENTA", "WHITE"]:
        color = getattr(Colors, name)
        print(f"{color}█ {name} {Colors.RESET}", end="  ")

    print("\n\nBright Colors:")
    for name in ["BRIGHT_RED", "BRIGHT_GREEN", "BRIGHT_YELLOW", "BRIGHT_CYAN"]:
        color = getattr(Colors, name)
        print(f"{color}█{Colors.RESET}", end="  {name} " )

    print("\n\nGradient Demo:")
    print(gradient_text("IBIS TRADING SYSTEM", ColorGradients.GOLD_GRADIENT))

    print("\nRainbow Demo:")
    print(rainbow_text("🦅 AUTONOMOUS GLOBAL INTELLIGENCE SYSTEM 🦅"))
