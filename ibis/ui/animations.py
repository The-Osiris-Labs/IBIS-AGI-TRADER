#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - ANIMATIONS 🦅               ║
║                                                                      ║
║              Animated Effects for Trading Dashboard                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import time
import threading
from typing import Callable, Optional
from datetime import datetime

from .colors import Colors


class LoadingAnimation:
    """Animated loading effects."""

    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    RADAR_FRAMES = ["◐", "◓", "◑", "◒", "◐", "◓"]
    DOTS_FRAMES = ["⠁", "⠂", "⠄", "⠂"]
    BAR_FRAMES = [
        "▁",
        "▂",
        "▃",
        "▄",
        "▅",
        "▆",
        "▇",
        "█",
        "▇",
        "▆",
        "▅",
        "▄",
        "▃",
        "▂",
        "▁",
    ]
    PULSE_FRAMES = ["◐", "◓", "◑", "◒"]
    WAVE_FRAMES = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"]

    def __init__(self, message: str = "Loading...", speed: float = 0.1):
        self.message = message
        self.speed = speed
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._frame_idx = 0

    def _animate_spinner(self):
        """Animate spinner."""
        while self.running:
            frame = self.SPINNER_FRAMES[self._frame_idx % len(self.SPINNER_FRAMES)]
            print(
                f"\r{Colors.CYAN}{frame} {self.message}...{Colors.RESET}",
                end="",
                flush=True,
            )
            time.sleep(self.speed)
            self._frame_idx += 1

    def _animate_radar(self):
        """Animate radar sweep."""
        while self.running:
            frame = self.RADAR_FRAMES[self._frame_idx % len(self.RADAR_FRAMES)]
            print(
                f"\r{Colors.CYAN}{frame} {self.message}{Colors.RESET}",
                end="",
                flush=True,
            )
            time.sleep(self.speed * 2)
            self._frame_idx += 1

    def _animate_dots(self):
        """Animate bouncing dots."""
        while self.running:
            frame = "".join(
                self.DOTS_FRAMES[(self._frame_idx + i) % len(self.DOTS_FRAMES)]
                for i in range(3)
            )
            print(
                f"\r{Colors.CYAN}{frame} {self.message}{Colors.RESET}",
                end="",
                flush=True,
            )
            time.sleep(self.speed)
            self._frame_idx += 1

    def start(self, style: str = "spinner"):
        """Start animation with specified style."""
        self.running = True
        self._frame_idx = 0

        animators = {
            "spinner": self._animate_spinner,
            "radar": self._animate_radar,
            "dots": self._animate_dots,
        }

        animator = animators.get(style, self._animate_spinner)
        self.thread = threading.Thread(target=animator)
        self.thread.start()

    def stop(self):
        """Stop animation."""
        self.running = False
        if self.thread:
            self.thread.join()
        print(f"\r{' ' * 50}\r", end="")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class ProgressAnimator:
    """Animated progress indicators."""

    @staticmethod
    def progress_bar(
        current: int,
        total: int,
        width: int = 40,
        message: str = "",
        show_percentage: bool = True,
    ) -> str:
        """Render progress bar string."""
        if total == 0:
            percent = 1.0
        else:
            percent = current / total

        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)

        if percent >= 1.0:
            color = Colors.GREEN
            status = "✓ Complete"
        elif percent >= 0.7:
            color = Colors.GREEN
            status = "⚡ Running"
        elif percent >= 0.3:
            color = Colors.YELLOW
            status = "⚙️ Processing"
        else:
            color = Colors.RED
            status = "▶️ Starting"

        pct_str = f" {percent * 100:.1f}%" if show_percentage else ""

        return f"{message}\n│{color}{bar}{Colors.RESET}│ {current}/{total}{pct_str} {status}"

    @staticmethod
    def scanning_animation(duration: float = 2.0, symbol: str = "markets"):
        """Show scanning radar animation."""
        frames = ["◐", "◓", "◑", "◒", "◐", "◓"]
        start = time.time()
        idx = 0

        while time.time() - start < duration:
            frame = frames[idx % len(frames)]
            elapsed = time.time() - start
            print(
                f"\r{Colors.CYAN}{frame} Scanning {symbol}... ({elapsed:.1f}s){Colors.RESET}",
                end="",
                flush=True,
            )
            time.sleep(0.1)
            idx += 1

        print(f"\r{' ' * 40}\r", end="")

    @staticmethod
    def countdown(seconds: int, message: str = "Starting in"):
        """Show countdown timer."""
        for i in range(seconds, 0, -1):
            print(
                f"\r{Colors.YELLOW}{message} {i}...{Colors.RESET}", end="", flush=True
            )
            time.sleep(1)
        print(f"\r{' ' * 30}\r", end="")

    @staticmethod
    def pulse(message: str = "●", interval: float = 0.5):
        """Pulse animation."""
        idx = 0
        while True:
            frames = ["●", "○", "◔", "◑", "◕", "◕"]
            frame = frames[idx % len(frames)]
            print(f"\r{Colors.CYAN}{frame} {message}{Colors.RESET}", end="", flush=True)
            time.sleep(interval)
            idx += 1


class PulseEffect:
    """Pulsing color effect for important elements."""

    def __init__(self, text: str, color: str = Colors.CYAN):
        self.text = text
        self.color = color
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _animate(self):
        """Animate pulsing."""
        idx = 0
        while self.running:
            intensities = ["[1m", "[2m", "[1m", "[2m"]
            intensity = intensities[idx % len(intensities)]
            print(
                f"\r{self.color}{intensity}{self.text}{Colors.RESET}",
                end="",
                flush=True,
            )
            time.sleep(0.3)
            idx += 1

    def start(self):
        """Start pulsing."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        """Stop pulsing."""
        self.running = False
        if self.thread:
            self.thread.join()
        print(f"\r{' ' * len(self.text) + 10}\r", end="")


class TypewriterEffect:
    """Typewriter text effect."""

    def __init__(self, text: str, speed: float = 0.02):
        self.text = text
        self.speed = speed

    def play(self, color: str = Colors.WHITE):
        """Play typewriter effect."""
        for char in self.text:
            print(f"{color}{char}{Colors.RESET}", end="", flush=True)
            if char not in " \n":
                time.sleep(self.speed / 10)
            else:
                time.sleep(self.speed)
        print()

    def play_centered(self, width: int = 80, color: str = Colors.WHITE):
        """Play centered typewriter effect."""
        lines = self.text.split("\n")
        for line in lines:
            padding = (width - len(line)) // 2
            print(" " * padding, end="")
            self.play(color)
            time.sleep(0.2)


class MarqueeText:
    """Scrolling marquee text effect."""

    def __init__(self, text: str, width: int = 60, speed: float = 0.1):
        self.text = text
        self.width = width
        self.speed = speed
        self.running = False

    def _animate(self):
        """Animate scrolling."""
        padded = " " * self.width + self.text + " " * self.width
        idx = 0

        while self.running:
            segment = padded[idx : idx + self.width]
            print(f"\r{Colors.CYAN}{segment}{Colors.RESET}", end="", flush=True)
            time.sleep(self.speed)
            idx = (idx + 1) % len(padded - self.width)

    def start(self):
        """Start scrolling."""
        self.running = True

    def stop(self):
        """Stop scrolling."""
        self.running = False
        print(f"\r{' ' * self.width}\r", end="")


class UptimeCounter:
    """Real-time uptime counter."""

    def __init__(self):
        self.start_time = None
        self.running = False

    def start(self):
        """Start counter."""
        self.start_time = datetime.now()
        self.running = True

    def get_formatted(self) -> str:
        """Get formatted uptime string."""
        if not self.start_time:
            return "00:00:00"

        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def stop(self):
        """Stop counter."""
        self.running = False


class CycleCounter:
    """Cycle counter with animation."""

    def __init__(self):
        self.cycle = 0
        self.symbols = [
            "▁",
            "▂",
            "▃",
            "▄",
            "▅",
            "▆",
            "▇",
            "█",
            "▇",
            "▆",
            "▅",
            "▄",
            "▃",
            "▂",
        ]
        self.idx = 0

    def next(self) -> str:
        """Get next symbol."""
        symbol = self.symbols[self.idx % len(self.symbols)]
        self.idx += 1
        return symbol

    def increment(self):
        """Increment cycle and advance symbol."""
        self.cycle += 1
        self.idx += 1

    def get_display(self) -> str:
        """Get cycle display."""
        return f"[{self.next()}] Cycle #{self.cycle}"


class ASCIIArt:
    """Static ASCII art assets."""

    IBIS_BANNER = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   {Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}   {Colors.BRIGHT_WHITE}███╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██████╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╗  ██╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔═══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ███╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║   ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██║     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚██████╔╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}╚═╝{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}╚═╝     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE} ╚═════╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}                                   ║
║                                                                              ║
║   {Colors.BRIGHT_YELLOW}AUTONOMOUS GLOBAL INTELLIGENCE SYSTEM{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.DIM}Version 5.5 - Ultra Enhanced{Colors.RESET}{Colors.BRIGHT_CYAN}                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""

    LOADING_FRAMES = [
        "▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁",
        "██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
        "▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    ]

    RADAR_FRAMES = ["◐", "◓", "◑", "◒"]

    @staticmethod
    def pulse_bar(percent: float, width: int = 20) -> str:
        """Create pulse bar."""
        filled = int(width * percent)
        empty = width - filled
        pulse = "█" * filled + "░" * empty
        if percent >= 0.8:
            color = Colors.GREEN
        elif percent >= 0.5:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        return f"{color}{pulse}{Colors.RESET}"


if __name__ == "__main__":
    print("🦅 Animation Demo")
    print("=" * 50)

    print("\nSpinner:")
    with LoadingAnimation("Processing", "spinner") as anim:
        time.sleep(2)

    print("\nRadar:")
    LoadingAnimation.scanning_animation(2, "opportunities")

    print("\nProgress Bar:")
    for i in range(0, 101, 10):
        print(
            f"\r{ProgressAnimator.progress_bar(i, 100, 40, 'Progress')}",
            end="",
            flush=True,
        )
        time.sleep(0.1)
    print()

    print("\nUptime Counter:")
    counter = UptimeCounter()
    counter.start()
    for i in range(5):
        print(f"\rUptime: {counter.get_formatted()}", end="", flush=True)
        time.sleep(1)
    print()
