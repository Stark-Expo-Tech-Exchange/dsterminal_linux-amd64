# edu_typing_engine.py

import sys
import time
import threading
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()


class EducationTypingEngine:

    def __init__(self, speed=0.03):
        self.speed = speed
        self.skip = False
        self.running = False

    def _listen(self):

        while self.running:
            key = sys.stdin.read(1)

            if key.lower() == "s":
                self.skip = True

            elif key.lower() == "f":
                self.speed = 0.005
                console.print("\n[yellow]⚡ Fast mode[/yellow]")

            elif key.lower() == "q":
                self.running = False
                console.print("\n[red]✖ Cancelled[/red]")
                break

    def type_text(self, text):

        self.running = True
        self.skip = False

        typed = ""

        listener = threading.Thread(
            target=self._listen,
            daemon=True
        )
        listener.start()

        with Live(refresh_per_second=20, console=console) as live:

            for ch in text:

                if not self.running:
                    break

                if self.skip:
                    typed = text
                    break

                typed += ch

                output = Text.from_markup(typed)

                status = Text(
                    "\n\n[dim]S=Skip  F=Fast  Q=Quit[/dim]"
                )

                live.update(output + status)

                time.sleep(self.speed)

        self.running = False

        console.print("\n[green]✔ Training complete[/green]\n")
