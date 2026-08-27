#!python
import sys
# -*- coding: utf-8 -*-
"""

# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass

_original_stdout_write = sys.stdout.write

def _safe_stdout_write(text):
    try:
        _original_stdout_write(text)
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

sys.stdout.write = _safe_stdout_write


# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass


    try:
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

sys.stdout.write = _safe_stdout_write

DSTerminal IOC Education Module
Standalone module for Indicators of Compromise education
Interactive random lesson generator - each run shows a different lesson
"""
import sys
import os
import time
import random
import shutil
import re
from typing import List, Optional, Dict, Any

# ============================================================
# FIX WINDOWS CONSOLE ENCODING - MUST BE FIRST
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
    # Fix stdout encoding
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        else:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except:
        pass

# ============================================================
# ANSI COLOR DEFINITIONS (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """ANSI color codes for terminal output"""
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTCYAN_EX = '\033[96m'
    LIGHTMAGENTA_EX = '\033[95m'
    LIGHTBLUE_EX = '\033[94m'
    LIGHTWHITE_EX = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BRIGHT = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True, convert=True, strip=False)
    COLORS_AVAILABLE = True
    # Force color support
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
except ImportError:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })

# ============================================================
# SIMPLE SAFE PRINT FUNCTION
# ============================================================
def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)
    except Exception:
        try:
            print(str(message))
        except:
            pass

# ============================================================
# CONTINUE WITH THE REST OF YOUR CODE
# ============================================================

class IOCEducation:
    """Indicators of Compromise Education Module - Interactive Random Lessons"""
    
    VERSION = "2.0.0"
    APP_NAME = "DSTerminal IOC Education"
    
    # Pen typing settings - CONSTANT SPEED
    PEN_SPEED = 0.035  # Seconds per character (35ms per char ≈ 28 chars/sec)
    PEN_VARIANCE = 0.008  # Small variance for natural feel
    AUTO_BREAK_CHARS = 80  # Characters before auto line break
    
    # Color schemes for random boxes
    COLOR_SCHEMES = [
        {'title': Fore.LIGHTCYAN_EX, 'border': Fore.LIGHTCYAN_EX, 'content': Fore.LIGHTGREEN_EX},
        {'title': Fore.LIGHTMAGENTA_EX, 'border': Fore.LIGHTMAGENTA_EX, 'content': Fore.LIGHTYELLOW_EX},
        {'title': Fore.LIGHTYELLOW_EX, 'border': Fore.LIGHTYELLOW_EX, 'content': Fore.LIGHTCYAN_EX},
        {'title': Fore.LIGHTGREEN_EX, 'border': Fore.LIGHTGREEN_EX, 'content': Fore.LIGHTWHITE_EX},
        {'title': Fore.LIGHTRED_EX, 'border': Fore.LIGHTRED_EX, 'content': Fore.LIGHTGREEN_EX},
        {'title': Fore.LIGHTBLUE_EX, 'border': Fore.LIGHTBLUE_EX, 'content': Fore.LIGHTYELLOW_EX},
        {'title': Fore.LIGHTWHITE_EX, 'border': Fore.LIGHTWHITE_EX, 'content': Fore.LIGHTCYAN_EX},
        {'title': Fore.LIGHTMAGENTA_EX, 'border': Fore.LIGHTCYAN_EX, 'content': Fore.LIGHTGREEN_EX},
    ]
    
    # ========================================================================
    # IOC LESSONS DATABASE - WITH EMOJIS (UTF-8)
    # ========================================================================
    
    IOC_LESSONS = [
        {
            "id": "lesson_1",
            "title": "📌 WHAT ARE INDICATORS OF COMPROMISE?",
            "icon": "🔍",
            "color_scheme": 0,
            "content": [
                "Indicators of Compromise (IOCs) are forensic artifacts that provide",
                "evidence of a potential security breach. They are the digital",
                "breadcrumbs left behind by attackers that security teams use to",
                "detect, investigate, and respond to cyber threats.",
                "",
                "💡 Think of IOCs like fingerprints at a crime scene - they don't",
                "tell you who committed the crime, but they prove that someone was",
                "there and help you track them down.",
                "",
                "📊 KEY CHARACTERISTICS:",
                "  • Observable - Can be detected by security tools",
                "  • Actionable - Can be used to make security decisions",
                "  • Verifiable - Can be confirmed through multiple sources",
                "  • Timely - Should be current and relevant",
                "",
                "🎯 Real-World Scenario:",
                "  A security analyst notices a suspicious file hash in the network",
                "  logs. They cross-reference it with threat intelligence feeds and",
                "  find it's associated with a known ransomware family. They use this",
                "  IOC to block the file across the entire organization, preventing",
                "  a potential ransomware outbreak."
            ]
        },
        # ... rest of the lessons remain the same ...
        # (Keep all the lesson data from your original file)
    ]
    
    def __init__(self, parent_terminal=None):
        """
        Initialize IOC Education Module.
        
        Args:
            parent_terminal: Reference to the main DSTerminal instance
        """
        self.parent = parent_terminal
        self.term_width = self._get_terminal_width()
        self.current_line_length = 0
        self.last_lesson_id = None
        self.lesson_history = []
        self.lessons_shown = 0
    
    def _get_terminal_width(self) -> int:
        """Get terminal width for centering"""
        try:
            width = shutil.get_terminal_size().columns
            if width < 80:
                return 80
            if width > 120:
                return 120
            return width
        except:
            return 80
    
    # ========================================================================
    # HUMAN-LIKE PEN TYPING ENGINE - CONSTANT SPEED
    # ========================================================================
    
    def _pen_type(self, text: str, color: Optional[str] = None, 
                  speed: Optional[float] = None, auto_break: bool = True,
                  indent: int = 0, newline: bool = True):
        """
        Human-like pen typing at CONSTANT speed with auto line breaks.
        """
        import sys
        import time
        import random
        
        delay = speed if speed is not None else self.PEN_SPEED
        
        if indent > 0:
            indent_text = " " * indent
            sys.stdout.write(indent_text)
            sys.stdout.flush()
            self.current_line_length += indent
        
        if color:
            sys.stdout.write(color)
            sys.stdout.flush()
        
        if auto_break and len(text) > self.AUTO_BREAK_CHARS:
            words = text.split()
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 > self.AUTO_BREAK_CHARS:
                    self._type_line(current_line.rstrip(), delay)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    if indent > 0:
                        sys.stdout.write(" " * indent)
                        sys.stdout.flush()
                    current_line = word + " "
                else:
                    current_line += word + " "
            
            if current_line:
                self._type_line(current_line.rstrip(), delay)
        else:
            self._type_line(text, delay)
        
        if color:
            sys.stdout.write(Style.RESET_ALL)
            sys.stdout.flush()
        
        if newline:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self.current_line_length = 0
    
    def _type_line(self, text: str, delay: float):
        """Type a single line with human-like rhythm at constant speed."""
        import sys
        import time
        import random
        
        for char in text:
            try:
                sys.stdout.write(char)
                sys.stdout.flush()
                self.current_line_length += 1
            except:
                pass
            
            try:
                if char in ".!?,":
                    time.sleep(delay * 1.8)
                elif char in ";:":
                    time.sleep(delay * 1.3)
                elif char == " ":
                    time.sleep(delay * 0.6)
                elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    time.sleep(delay * 1.15)
                else:
                    time.sleep(delay + (random.random() - 0.5) * self.PEN_VARIANCE)
            except:
                time.sleep(delay)
    
    # ========================================================================
    # HACKER-STYLE BOX DRAWING WITH PEN TYPING
    # ========================================================================
    
    def _draw_pen_box(
        self,
        title: str,
        content_lines: List[str],
        title_color: str,
        border_color: str,
        content_color: Optional[str] = None,
        width: Optional[int] = None,
        speed: Optional[float] = None
    ):
        """
        Draw a hacker-styled centered box with human-like pen typing.
        """
        import textwrap
        
        content_color = content_color or Fore.GREEN
        pen_speed = speed if speed is not None else self.PEN_SPEED
        
        try:
            term = shutil.get_terminal_size((100, 30))
            term_width = term.columns
        except:
            term_width = 80
        
        if width is None:
            width = min(term_width - 6, 110)
        
        width = max(width, 60)
        left_margin = max(0, (term_width - width) // 2)
        inner = width - 4
        
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            try:
                wrapped.extend(
                    textwrap.wrap(
                        line,
                        inner,
                        break_long_words=False,
                        replace_whitespace=False
                    )
                )
            except:
                wrapped.append(line[:inner])
        
        top = "╔" + "═" * (width - 2) + "╗"
        mid = "╠" + "═" * (width - 2) + "╣"
        bot = "╚" + "═" * (width - 2) + "╝"
        
        print()
        print(" " * left_margin + border_color + top)
        
        title_text = f" {title} "
        print(" " * left_margin + title_color + "║", end="")
        self._pen_type(
            title_text.center(width - 2) + "║",
            color=title_color,
            speed=pen_speed * 0.5,
            newline=False
        )
        
        print(" " * left_margin + border_color + mid)
        
        for line in wrapped:
            print(" " * left_margin + border_color + "║ " + Style.RESET_ALL, end="")
            self._pen_type(
                line.ljust(inner),
                color=content_color,
                speed=pen_speed,
                newline=False
            )
            print(" " * left_margin + border_color + "║")
        
        print(" " * left_margin + border_color + bot)
        print()
        time.sleep(pen_speed * 1.5)
    
    # ========================================================================
    # RANDOM LESSON GENERATOR
    # ========================================================================
    
    def _get_random_lesson(self) -> Dict:
        """Get a random lesson, avoiding the last one and history."""
        # Get lessons not yet shown in this session
        available_lessons = [l for l in self.IOC_LESSONS if l["id"] not in self.lesson_history]
        
        # If all lessons have been shown, reset history
        if not available_lessons:
            self.lesson_history = []
            available_lessons = self.IOC_LESSONS
        
        # Remove the last lesson to avoid repetition
        if self.last_lesson_id:
            available_lessons = [l for l in available_lessons if l["id"] != self.last_lesson_id]
            
            # If only one lesson left and it's the last one, allow it
            if not available_lessons:
                available_lessons = [l for l in self.IOC_LESSONS if l["id"] != self.last_lesson_id]
                if not available_lessons:
                    available_lessons = self.IOC_LESSONS
        
        lesson = random.choice(available_lessons)
        self.last_lesson_id = lesson["id"]
        self.lesson_history.append(lesson["id"])
        self.lessons_shown += 1
        
        return lesson
    
    def _get_color_scheme(self, index: int) -> Dict:
        """Get a color scheme by index, with random fallback."""
        if index < len(self.COLOR_SCHEMES):
            return self.COLOR_SCHEMES[index]
        return random.choice(self.COLOR_SCHEMES)
    
    # ========================================================================
    # INTERACTIVE LESSON DISPLAY
    # ========================================================================
    
    def _show_continue_prompt(self, total_lessons: int, lessons_shown: int) -> bool:
        """
        Show interactive prompt asking if user wants to continue learning.
        Returns True if they want to continue, False if they want to exit.
        """
        # Build prompt content
        remaining = total_lessons - lessons_shown
        
        prompt_lines = [
            f"📊 Progress: {lessons_shown}/{total_lessons} lessons completed",
            f"📖 Remaining: {remaining} lessons available",
            "",
            "Would you like to continue learning about IOCs?"
        ]
        
        if remaining == 0:
            prompt_lines = [
                "🎉 You've completed all available lessons!",
                "",
                "Would you like to review a random lesson again?"
            ]
        
        self._draw_pen_box(
            "📖 CONTINUE LEARNING?",
            prompt_lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=None,
            speed=self.PEN_SPEED
        )
        
        # Get user input with clear options
        try:
            print(f"\n{Fore.CYAN}┌─ {Fore.YELLOW}Select option {Fore.CYAN}─►{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}[Y]{Style.RESET_ALL} Yes, show me another lesson")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}[N]{Style.RESET_ALL} No, I'm done for now")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}[L]{Style.RESET_ALL} List all available lessons")
            print(f"{Fore.CYAN}└─ {Fore.MAGENTA}Your choice {Fore.CYAN}►{Style.RESET_ALL} ", end="")
            
            choice = input().strip().lower()
        except:
            choice = 'n'
        
        if choice == 'l':
            self._list_lessons()
            return self._show_continue_prompt(total_lessons, lessons_shown)
        elif choice == 'y' or choice == 'yes':
            return True
        else:
            return False
    
    def _list_lessons(self):
        """Display a list of all available lessons."""
        lessons_list = []
        for i, lesson in enumerate(self.IOC_LESSONS, 1):
            status = "✅" if lesson["id"] in self.lesson_history else "📖"
            lessons_list.append(f"{status} Lesson {i}: {lesson['icon']} {lesson['title']}")
        
        self._draw_pen_box(
            "📚 ALL AVAILABLE LESSONS",
            lessons_list,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=None,
            speed=self.PEN_SPEED
        )
    
    # ========================================================================
    # MAIN INTERACTIVE RUN
    # ========================================================================
    
    def run_interactive(self, speed: Optional[float] = None):
        """
        Run interactive lesson mode - shows random lessons and asks if user wants to continue.
        """
        pen_speed = speed if speed is not None else self.PEN_SPEED
        self.lesson_history = []
        self.lessons_shown = 0
        self.last_lesson_id = None
        
        total_lessons = len(self.IOC_LESSONS)
        
        try:
            print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.LIGHTGREEN_EX}🛡️  INTERACTIVE IOC EDUCATION  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Learn at your own pace{Fore.CYAN}  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        except:
            print("\n=== INTERACTIVE IOC EDUCATION ===")
            print("Learn at your own pace")
        
        time.sleep(0.5)
        
        while True:
            try:
                # Show a random lesson
                self.show_random_lesson(speed=pen_speed, auto_continue=False)
                
                # Ask if user wants to continue
                should_continue = self._show_continue_prompt(total_lessons, self.lessons_shown)
                
                if not should_continue:
                    break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        # Farewell message
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
        
        farewell_content = [
            f"🎓 You completed {self.lessons_shown} lessons today!",
            "",
            "🛡️ Remember:",
            "  • IOCs are digital breadcrumbs left by attackers",
            "  • Use them to detect, investigate, and respond",
            "  • Share intelligence with the security community",
            "",
            "📚 You can always run this module again to:",
            "  • Review any lesson",
            "  • Learn new topics",
            "  • Stay updated on IOC best practices",
            "",
            "💡 Keep learning, stay secure!",
            "",
            "Press Enter to exit..."
        ]
        
        self._draw_pen_box(
            "🎉 LEARNING COMPLETE",
            farewell_content,
            title_color=Fore.LIGHTGREEN_EX,
            border_color=Fore.LIGHTGREEN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=None,
            speed=pen_speed
        )
        try:
            input()
        except:
            pass
    
    def show_random_lesson(self, speed: Optional[float] = None, auto_continue: bool = False):
        """
        Display a random IOC lesson with unique color scheme.
        Each run shows a different lesson.
        """
        pen_speed = speed if speed is not None else self.PEN_SPEED
        
        # Clear screen
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
        
        # Get random lesson
        lesson = self._get_random_lesson()
        color_scheme = self._get_color_scheme(lesson["color_scheme"])
        
        # Get terminal width for centering
        try:
            term_width = os.get_terminal_size().columns
            box_width = min(term_width - 4, 100)
            box_width = max(box_width, 60)
        except:
            box_width = 80
        
        # ============================================================
        # HEADER
        # ============================================================
        header_art = [
            "  ██╗  ██╗ ██████╗  ██████╗██╗  ██╗",
            "  ██║  ██║██╔═══██╗██╔════╝██║  ██║",
            "  ███████║██║   ██║██║     ███████║",
            "  ██╔══██║██║   ██║██║     ██╔══██║",
            "  ██║  ██║╚██████╔╝╚██████╗██║  ██║",
            "  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝"
        ]
        
        total_lessons = len(self.IOC_LESSONS)
        lesson_num = self.IOC_LESSONS.index(lesson) + 1
        
        self._draw_pen_box(
            f"🛡️ IOC EDUCATION - LESSON {lesson_num}/{total_lessons}",
            header_art + ["", f"💻 {self.APP_NAME} v{self.VERSION}"],
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTGREEN_EX,
            width=box_width,
            speed=pen_speed * 0.3
        )
        time.sleep(0.3)
        
        # ============================================================
        # MAIN LESSON CONTENT
        # ============================================================
        self._draw_pen_box(
            f"{lesson['icon']} {lesson['title']}",
            lesson["content"],
            title_color=color_scheme['title'],
            border_color=color_scheme['border'],
            content_color=color_scheme['content'],
            width=box_width,
            speed=pen_speed
        )
        
        # ============================================================
        # FOOTER WITH PROGRESS
        # ============================================================
        footer_content = [
            f"📖 Lessons Completed: {self.lessons_shown}/{total_lessons}",
            f"📚 Remaining: {total_lessons - self.lessons_shown}",
            "",
        ]
        
        if auto_continue:
            footer_content.append("⏳ Continuing to next lesson in 3 seconds...")
        else:
            footer_content.append("💡 Press Enter to continue...")
        
        self._draw_pen_box(
            "📊 PROGRESS",
            footer_content,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=box_width,
            speed=pen_speed
        )
        
        if not auto_continue:
            try:
                input()
            except:
                pass
    
    def run(self, speed: Optional[float] = None, interactive: bool = True):
        """
        Main execution method - called from DSTerminal.
        
        Args:
            speed: Optional typing speed override
            interactive: If True, runs in interactive mode with continue prompts
        """
        if interactive:
            self.run_interactive(speed)
        else:
            self.show_random_lesson(speed)


# ========================================================================
# STANDALONE EXECUTION
# ========================================================================

def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='IOC Education Module - Interactive Learning')
    parser.add_argument('--all', action='store_true', help='Show all lessons sequentially (non-interactive)')
    parser.add_argument('--list', action='store_true', help='List all available lessons')
    parser.add_argument('--speed', type=float, default=0.035, 
                       help='Typing speed in seconds per character (default: 0.035)')
    parser.add_argument('--non-interactive', action='store_true', 
                       help='Run without interactive prompts (show one random lesson)')
    args = parser.parse_args()
    
    try:
        print(f"{Fore.CYAN}DSTerminal IOC Education Module v{IOCEducation.VERSION}{Style.RESET_ALL}")
    except:
        print(f"DSTerminal IOC Education Module v{IOCEducation.VERSION}")
    
    time.sleep(0.5)
    
    if args.list:
        try:
            print(f"\n{Fore.YELLOW}Available Lessons:{Style.RESET_ALL}")
        except:
            print("\nAvailable Lessons:")
        for i, lesson in enumerate(IOCEducation.IOC_LESSONS, 1):
            try:
                print(f"  {i}. {lesson['icon']} {lesson['title']}")
            except:
                print(f"  {i}. {lesson['title']}")
        try:
            print(f"\n{Fore.CYAN}Total: {len(IOCEducation.IOC_LESSONS)} lessons{Style.RESET_ALL}")
        except:
            print(f"\nTotal: {len(IOCEducation.IOC_LESSONS)} lessons")
        return
    
    ioc = IOCEducation()
    
    if args.all:
        # Show all lessons sequentially
        for lesson in ioc.IOC_LESSONS:
            ioc.show_random_lesson(speed=args.speed, auto_continue=True)
            time.sleep(3)
    elif args.non_interactive:
        ioc.show_random_lesson(speed=args.speed)
    else:
        # Interactive mode with continue prompts
        ioc.run_interactive(speed=args.speed)


if __name__ == "__main__":
    main()