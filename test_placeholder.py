#!/usr/bin/env python3
"""
DSTerminal Placeholder Animation Test Script
With TypeWriter Autotyping Effect on Prompt
"""

import sys
import time
import random
import threading
from datetime import datetime

# Import prompt_toolkit components
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.processors import Processor, Transformation
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import processors
from prompt_toolkit.formatted_text import FormattedText

# ============================================================
# COLORS CLASS
# ============================================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLACK = '\033[90m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    DIM = '\033[2m'
    
    @staticmethod
    def strip(text):
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TYPEWRITER CLASS (from web_security_analyzer.py)
# ============================================================

class TypeWriter:
    """Human-like typing simulation with pen writing effects"""
    
    def __init__(self, speed='fast'):
        self.speed_presets = {
            'slow': (30, 60),
            'medium': (15, 35),
            'fast': (5, 15),
            'instant': (0, 0)
        }
        self.set_speed(speed)
        self.punctuation_delay = 1.5
        self.typing_enabled = True
        self._stop_typing = False
        self.current_color = Colors.GREEN
        self.use_colors = True
        
    def set_speed(self, speed):
        if speed in self.speed_presets:
            self.min_delay, self.max_delay = self.speed_presets[speed]
        else:
            self.min_delay, self.max_delay = self.speed_presets['fast']
    
    def type_text(self, text, color=Colors.GREEN, newline=True, pause_between_chars=True, 
                  pen_effect=True, line_by_line=False):
        """Type text with human-like pen writing simulation"""
        
        if not self.typing_enabled:
            print(f"{text}", end='\n' if newline else '')
            return
        
        if line_by_line:
            lines = text.split('\n')
            for line in lines:
                self._type_line(line, color, pause_between_chars, pen_effect)
                if newline:
                    print()
                time.sleep(random.uniform(0.1, 0.3))
            return
        
        self._type_line(text, color, pause_between_chars, pen_effect)
        if newline:
            print()
    
    def _type_line(self, text, color, pause_between_chars, pen_effect):
        """Type a single line with pen effects"""
        
        pause_chars = ['.', ',', '!', '?', ';', ':', '...', '—', '–']
        
        for i, char in enumerate(text):
            if self._stop_typing:
                break
            
            if char == '\n':
                print()
                continue
            else:
                if self.use_colors and color and pen_effect and (i == 0 or text[i-1] == ' '):
                    sys.stdout.write(f"{Colors.BOLD}{color}{char}{Colors.END}")
                elif self.use_colors and color:
                    sys.stdout.write(f"{color}{char}{Colors.END}")
                else:
                    sys.stdout.write(char)
                sys.stdout.flush()
            
            if self.min_delay == 0 and self.max_delay == 0:
                delay = 0
            else:
                # Base delay with some randomness
                delay = random.uniform(self.min_delay, self.max_delay) / 1000.0
                
                # Pen effect: slightly longer after punctuation
                if char in pause_chars and pause_between_chars:
                    delay *= self.punctuation_delay
                
                # Random hesitation (like thinking)
                if random.random() < 0.03:
                    delay += random.uniform(50, 200) / 1000.0
                
                # Faster typing after spaces (like natural rhythm)
                if char == ' ':
                    delay *= 0.7
                
                # Slower on numbers/symbols (like thinking)
                if char.isdigit() or char in ['@', '#', '$', '%', '^', '&', '*']:
                    delay *= 1.3
            
            time.sleep(delay)
    
    def type_line(self, text, color=Colors.GREEN, pen_effect=True):
        """Type a single line with newline"""
        self.type_text(text, color, newline=True, pen_effect=pen_effect)
    
    def type_block(self, lines, color=Colors.GREEN, delay_between_lines=0.3, pen_effect=True):
        """Type multiple lines with delays between them"""
        for line in lines:
            self.type_text(line, color, newline=True, pen_effect=pen_effect)
            if delay_between_lines > 0:
                time.sleep(delay_between_lines)
    
    def type_banner(self, lines, color=Colors.CYAN, delay_between=0.1):
        """Type banner with faster typing speed"""
        original_speed = self.min_delay, self.max_delay
        self.min_delay, self.max_delay = 2, 5  # Fast for banners
        
        for line in lines:
            self.type_text(line, color, newline=True, pen_effect=False)
            time.sleep(delay_between)
        
        self.min_delay, self.max_delay = original_speed
    
    def type_animated(self, text, color=Colors.GREEN, duration=0.5):
        """Type with animated cursor effect"""
        if not self.typing_enabled:
            print(f"{text}")
            return
        
        cursor_chars = ['|', '/', '-', '\\']
        cursor_idx = 0
        
        display_text = text if self.use_colors else Colors.strip(text)
        
        for i in range(len(display_text) + 1):
            if self._stop_typing:
                break
            
            sys.stdout.write('\r')
            if self.use_colors and color:
                sys.stdout.write(f"{color}{display_text[:i]}{Colors.DIM}{cursor_chars[cursor_idx % len(cursor_chars)]}{Colors.END}")
            else:
                sys.stdout.write(f"{display_text[:i]}{cursor_chars[cursor_idx % len(cursor_chars)]}")
            sys.stdout.flush()
            
            cursor_idx += 1
            time.sleep(duration / (len(display_text) + 1))
        
        sys.stdout.write('\r')
        if self.use_colors and color:
            sys.stdout.write(f"{color}{display_text}{Colors.END}")
        else:
            sys.stdout.write(display_text)
        sys.stdout.flush()
        print()
    
    def stop_typing(self):
        self._stop_typing = True
    
    def reset(self):
        self._stop_typing = False

# ============================================================
# CUSTOM PLACEHOLDER PROCESSOR WITH RANDOM COLORS
# ============================================================

class PlaceholderProcessor(Processor):
    """Processor that adds placeholder text to empty buffer with random colors"""
    
    def __init__(self, get_placeholder_data):
        self.get_placeholder_data = get_placeholder_data
    
    def apply_transformation(self, transformation_input):
        # Only show placeholder when buffer is empty
        if transformation_input.document.text:
            return Transformation(transformation_input.fragments)
        
        placeholder_data = self.get_placeholder_data()
        if not placeholder_data or not placeholder_data['text']:
            return Transformation(transformation_input.fragments)
        
        # Create formatted text with each character having its own color
        formatted = []
        for char, color in placeholder_data['colored_chars']:
            if color:
                formatted.append((f'fg:{color}', char))
            else:
                formatted.append(('', char))
        
        return Transformation(formatted)

# ============================================================
# PLACEHOLDER TEST TERMINAL WITH TYPEWRITER
# ============================================================

class PlaceholderTestTerminal:
    def __init__(self):
        self.cursor_running = False
        self.cursor_thread = None
        self.cursor_visible = True
        self.cursor_color_index = 0
        self.cursor_colors = ['#00ff88', '#00ccff', '#ff00ff', '#ffcc00']
        self.start_time = datetime.now()
        self.placeholder_visible = ""
        self.placeholder_colors = []  # List of (char, color) tuples
        self.current_sentence = ""
        self.char_index = 0
        self.phase = "typing"
        self.placeholder_lock = threading.Lock()
        self.user_typing = False  # Track if user is typing
        self.stop_animation = False  # Stop flag for animation
        self.typer = TypeWriter('fast')
        self.app = None  # Will be set after session creation
        
        # Color palette for placeholder text
        self.color_palette = [
            '#ff6b6b',  # Red
            '#ffa94d',  # Orange
            '#ffd93d',  # Yellow
            '#6bcb77',  # Green
            '#4d96ff',  # Blue
            '#9b59b6',  # Purple
            '#ff6b9d',  # Pink
            '#00d2d3',  # Cyan
            '#f368e0',  # Magenta
            '#ff9ff3',  # Light Pink
            '#54a0ff',  # Light Blue
            '#5f27cd',  # Dark Purple
            '#01a3a4',  # Teal
            '#f8a5c2',  # Rose
            '#778beb',  # Periwinkle
        ]
        
        self.sentences = [
            "Type 'help' to see commands, or start typing...",
            "Good morning, Analyst. Ready to secure the network?",
            "What security task shall we tackle today?",
            "Feeling curious? Try 'system scan' or 'net mon'.",
            "Ready to hunt for threats? Type 'soc status'.",
            "Stay vigilant. Type 'dashboard' to monitor live data.",
            "What's on your security agenda today?",
            "Network quiet. Time for some recon? Try 'recon'.",
            "Hello, Defender. Type 'help' for a full command list.",
            "Need to check for vulnerabilities? Type 'vuln-scan'.",
            "The terminal is ready. What's your command?",
            "Shall we harden the system today? Type 'harden'.",
            "Looking for threats? Type 'ransomwatch'.",
            "Good afternoon! Ready for some advanced forensics?",
            "Remember: Always verify. Type 'integrity scan'.",
            "Feeling creative? Try 'crypto-verify' or 'stegcheck'.",
            "Let's keep the systems secure. Type 'status'.",
            "Your cybersecurity hub awaits. What's next?",
            "Ready to dive into the logs? Type 'dst-logs'.",
            "Type 'exit' to close, or 'help' to explore the universe."
        ]

    def _start_cursor_blink(self):
        self.cursor_running = True
        self.cursor_thread = threading.Thread(target=self._animate_cursor, daemon=True)
        self.cursor_thread.start()

    def _animate_cursor(self):
        while self.cursor_running:
            self.cursor_visible = not self.cursor_visible
            if not self.cursor_visible:
                self.cursor_color_index = (self.cursor_color_index + 1) % len(self.cursor_colors)
            # Invalidate app to update cursor
            if self.app:
                self.app.invalidate()
            time.sleep(0.5)

    def _get_cursor_char(self) -> str:
        return "▌" if self.cursor_visible else " "

    def _get_cursor_color(self) -> str:
        return self.cursor_colors[self.cursor_color_index]
    
    def _get_uptime(self) -> str:
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

    # ============================================================
    # TYPEWRITER ANIMATION FOR PROMPT PLACEHOLDER
    # ============================================================
    def _get_random_color(self) -> str:
        """Get a random color from the palette"""
        return random.choice(self.color_palette)
    
    def _type_placeholder(self, text):
        """Type placeholder text with pen-writing effect and random colors"""
        with self.placeholder_lock:
            self.placeholder_visible = ""
            self.placeholder_colors = []
        
        for i, char in enumerate(text):
            # Check if user started typing or animation should stop
            if self.user_typing or self.stop_animation:
                break
            
            # Get random color for this character
            color = self._get_random_color()
            
            with self.placeholder_lock:
                self.placeholder_visible = text[:i+1]
                self.placeholder_colors.append((char, color))
            
            # Invalidate app to redraw prompt
            if self.app:
                self.app.invalidate()
            
            # Natural typing delay
            delay = random.uniform(0.02, 0.08)
            
            # Pause longer after punctuation
            if char in ['.', ',', '!', '?', ';', ':']:
                delay *= 2.0
            
            # Random hesitation
            if random.random() < 0.03:
                delay += random.uniform(0.1, 0.3)
            
            # Faster after spaces
            if char == ' ':
                delay *= 0.6
            
            # Slower on special characters
            if char in ['@', '#', '$', '%', '^', '&', '*', '(', ')']:
                delay *= 1.5
            
            time.sleep(delay)
    
    def _erase_placeholder(self):
        """Erase placeholder text with pen-writing effect"""
        while True:
            # Check if user started typing or animation should stop
            if self.user_typing or self.stop_animation:
                break
            
            with self.placeholder_lock:
                if len(self.placeholder_visible) == 0:
                    break
                self.placeholder_visible = self.placeholder_visible[:-1]
                if self.placeholder_colors:
                    self.placeholder_colors.pop()
            
            # Invalidate app to redraw prompt
            if self.app:
                self.app.invalidate()
            
            time.sleep(random.uniform(0.01, 0.03))

    def _animate_placeholder(self):
        """Auto-type placeholder text with natural typing effect"""
        while self.cursor_running and not self.stop_animation:
            if self.user_typing:
                time.sleep(0.1)
                continue
            
            # Pick random sentence
            sentence = random.choice(self.sentences)
            
            # Type it with pen effect
            self._type_placeholder(sentence)
            
            if self.user_typing or self.stop_animation:
                continue
            
            # Pause after typing
            time.sleep(random.uniform(1.0, 2.5))
            
            if self.user_typing or self.stop_animation:
                continue
            
            # Erase with pen effect
            self._erase_placeholder()
            
            if self.user_typing or self.stop_animation:
                continue
            
            # Idle before next sentence
            time.sleep(random.uniform(0.5, 1.5))

    # ============================================================
    # GET PLACEHOLDER FOR PROCESSOR
    # ============================================================
    
    def get_placeholder_data(self) -> dict:
        """Return current placeholder text and colors"""
        with self.placeholder_lock:
            if self.user_typing:
                return {'text': '', 'colored_chars': []}
            return {
                'text': self.placeholder_visible,
                'colored_chars': self.placeholder_colors
            }

    # ============================================================
    # PROMPT BUILDER
    # ============================================================

    def _get_prompt(self) -> HTML:
        timestamp = datetime.now().strftime("%H:%M:%S")
        cursor_char = self._get_cursor_char()
        cursor_color = self._get_cursor_color()
        
        return HTML(
            f"<ansiwhite>┌─[</ansiwhite>"
            f"<ansiyellow>{timestamp}</ansiyellow>"
            f"<ansiwhite>]</ansiwhite> "
            f"<ansicyan>📊</ansicyan> "
            f"<ansigreen>SIEM=>DSTERMINAL CYBER-OPS</ansigreen> "
            f"<ansiwhite>v4.0.0.113</ansiwhite>\n"
            f"<ansiwhite>├─</ansiwhite> "
            f"<ansiyellow>Alerts:</ansiyellow> "
            f"<ansigreen>150</ansigreen> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Critical:</ansiyellow> "
            f"<ansigreen>10</ansigreen> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>High:</ansiyellow> "
            f"<ansigreen>40</ansigreen>\n"
            f"<ansiwhite>├─</ansiwhite> "
            f"<ansiyellow>Incidents:</ansiyellow> "
            f"<ansigreen>12</ansigreen> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Uptime:</ansiyellow> "
            f"<ansigreen>{self._get_uptime()}</ansigreen>\n"
            f"<ansiwhite>└─</ansiwhite>"
            f"<ansired>❯</ansired> "
            f"<style color='{cursor_color}'>{cursor_char}</style> "
        )

    def run(self):
        self._start_cursor_blink()
        
        # Create placeholder processor
        placeholder_processor = PlaceholderProcessor(self.get_placeholder_data)
        
        # Create session with the placeholder processor
        self.session = PromptSession(
            history=FileHistory('.test_history'),
            style=Style([('bottom-toolbar', 'bg:#1a1a2e #33ff33')]),
            reserve_space_for_menu=0,
            complete_while_typing=True,
            input_processors=[placeholder_processor],
        )
        
        # Get the application reference
        self.app = self.session.app
        
        # Watch buffer for changes
        buffer = self.session.default_buffer
        
        def on_text_changed(_):
            """Detect when buffer content changes"""
            text = buffer.text
            
            with self.placeholder_lock:
                if text:
                    # User is typing - hide placeholder
                    self.user_typing = True
                    self.placeholder_visible = ""
                    self.placeholder_colors = []
                else:
                    # Buffer is empty - resume placeholder
                    self.user_typing = False
            
            # Redraw prompt
            if self.app:
                self.app.invalidate()
        
        buffer.on_text_changed += on_text_changed
        
        # Start auto-typing animation loop
        anim_thread = threading.Thread(target=self._animate_placeholder, daemon=True)
        anim_thread.start()
        
        # Welcome message
        print("\n")
        print("=" * 60)
        print("🧪 DSTERMINAL PLACEHOLDER TEST [PEN-TYPING MODE]")
        self.typer.type_text("The prompt placeholder will auto-type with random colored characters!", 
                            color=Colors.GREEN, pen_effect=True)
        self.typer.type_text("Placeholder disappears when you start typing.", 
                            color=Colors.YELLOW, pen_effect=True)
        self.typer.type_text("Type 'exit' to quit.", 
                            color=Colors.CYAN, pen_effect=True)
        print("=" * 60 + "\n")
        
        try:
            while True:
                prompt_text = self._get_prompt()
                user_input = self.session.prompt(prompt_text)
                
                if user_input.lower() == "exit":
                    self.typer.type_text("\nGoodbye! 👋", color=Colors.CYAN, pen_effect=True)
                    break
                
                print(f"✅ You typed: {user_input}")
                
        except KeyboardInterrupt:
            print("\n\nExiting test...")
        finally:
            self.stop_animation = True
            self.cursor_running = False


if __name__ == "__main__":
    terminal = PlaceholderTestTerminal()
    terminal.run()