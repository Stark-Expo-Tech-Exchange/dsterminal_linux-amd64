#!python
# edu_typing_engine.py
import sys
import time
import threading
from rich.console import Console
from rich.live import Live
from rich.text import Text

# ============================================================
# FIX: Use a non-blocking approach for stdin
# ============================================================

console = Console()

class EducationTypingEngine:
    def __init__(self, speed=0.03):
        self.speed = speed
        self.skip = False
        self.running = False

    def _listen(self):
        """Listen for keyboard input without blocking the main thread"""
        while self.running:
            try:
                # Use a timeout to avoid blocking indefinitely
                if sys.stdin.isatty():
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if not key:
                            continue
                        if key.lower() == "s":
                            self.skip = True
                        elif key.lower() == "f":
                            self.speed = 0.005
                            console.print("\n[yellow]⚡ Fast mode[/yellow]")
                        elif key.lower() == "q":
                            self.running = False
                            console.print("\n[red]✖ Cancelled[/red]")
                            break
                else:
                    # If stdin is not a tty (e.g., redirected), just sleep
                    time.sleep(0.1)
            except:
                # Silently handle any errors
                time.sleep(0.1)

    def type_text(self, text):
        self.running = True
        self.skip = False
        typed = ""

        listener = threading.Thread(target=self._listen, daemon=True)
        listener.start()

        try:
            with Live(refresh_per_second=20, console=console) as live:
                for ch in text:
                    if not self.running:
                        break
                    if self.skip:
                        typed = text
                        break
                    typed += ch
                    output = Text.from_markup(typed)
                    status = Text("\n\n[dim]S=Skip  F=Fast  Q=Quit[/dim]")
                    live.update(output + status)
                    time.sleep(self.speed)
        except Exception as e:
            # Handle any Live display errors gracefully
            console.print(f"[dim]Typing display error: {e}[/dim]")
            # Fallback to simple print
            print(text)

        self.running = False
        listener.join(timeout=1)
        console.print("\n[green]✔ Training complete[/green]\n")