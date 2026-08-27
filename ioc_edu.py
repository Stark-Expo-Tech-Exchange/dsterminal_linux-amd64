#!/usr/bin/env python3
"""
DSTerminal IOC Education Module
Standalone module for Indicators of Compromise education
Interactive random lesson generator - each run shows a different lesson
"""

import os
import sys
import time
import random
import shutil
import re
from typing import List, Optional, Dict, Any

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    # Fallback color codes
    class Fore:
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
    
    class Style:
        RESET_ALL = '\033[0m'
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
    
    COLORS_AVAILABLE = False


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
    # IOC LESSONS DATABASE
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
        {
            "id": "lesson_2",
            "title": "⚡ IOC vs IOA - UNDERSTANDING THE DIFFERENCE",
            "icon": "⚡",
            "color_scheme": 1,
            "content": [
                "Many security professionals confuse IOCs with IOAs, but they serve",
                "different purposes in the security lifecycle.",
                "",
                "🔍 IOC (Indicator of Compromise) - PAST/FORENSIC",
                "  • Evidence that an attack has ALREADY happened",
                "  • Things you look for AFTER a breach",
                "  • Example: Malware hash, malicious domain, changed registry keys",
                "  • Question: 'What did the attacker leave behind?'",
                "",
                "⚡ IOA (Indicator of Attack) - PRESENT/ACTIVE",
                "  • Evidence that an attack is HAPPENING RIGHT NOW",
                "  • Things you look for DURING an active attack",
                "  • Example: Unusual login attempts, data exfiltration, privilege escalation",
                "  • Question: 'What is the attacker doing right now?'",
                "",
                "🎯 Real-World Scenario:",
                "  An organization detects an IOA when they see a user account",
                "  making multiple failed login attempts followed by a successful login",
                "  from an unusual location. Meanwhile, IOCs would be the malicious",
                "  IP addresses and domains that the attacker used, discovered after",
                "  the investigation begins.",
                "",
                "🎯 BOTH are essential for a complete security strategy!",
                "  IOCs help you detect past attacks, IOAs help you stop attacks in progress."
            ]
        },
        {
            "id": "lesson_3",
            "title": "📋 TYPES OF INDICATORS OF COMPROMISE",
            "icon": "📋",
            "color_scheme": 2,
            "content": [
                "There are many types of IOCs that security teams monitor:",
                "",
                "🔑 1. FILE HASHES (MD5, SHA-1, SHA-256)",
                "  • Unique fingerprint of a file",
                "  • Example: 5d41402abc4b2a76b9719d911017c592",
                "  • Use: Identify known malware by hash",
                "",
                "🌐 2. DOMAINS",
                "  • Malicious websites used for C2, phishing",
                "  • Example: malicious-phishing-site.com",
                "  • Use: Block domains in DNS or proxy",
                "",
                "📍 3. IP ADDRESSES",
                "  • Command & Control (C2) servers",
                "  • Example: 185.130.5.253",
                "  • Use: Block IPs in firewall",
                "",
                "🔗 4. URLs",
                "  • Specific malicious web addresses",
                "  • Example: http://bad-site.com/payload.exe",
                "  • Use: Block URLs in web filter",
                "",
                "📁 5. FILE PATHS",
                "  • Locations where malware is installed",
                "  • Example: C:\\Windows\\Temp\\malware.exe",
                "  • Use: Delete suspicious files",
                "",
                "🔧 6. REGISTRY KEYS (Windows)",
                "  • Persistence mechanisms",
                "  • Example: HKLM\\Software\\Microsoft\\Windows\\Run\\Evil",
                "  • Use: Remove malicious registry entries",
                "",
                "🧠 7. PROCESS NAMES",
                "  • Known malicious processes",
                "  • Example: cryptolocker.exe",
                "  • Use: Kill suspicious processes",
                "",
                "📧 8. EMAIL ADDRESSES",
                "  • Phishing sender addresses",
                "  • Example: security@fake-update.com",
                "  • Use: Block sender in email filter",
                "",
                "🎯 Real-World Scenario:",
                "  A security team receives an alert about a suspicious file. They",
                "  collect the file hash (SHA-256) and check it against VirusTotal.",
                "  They find it's a known ransomware variant. They also extract the",
                "  C2 domain from the malware and the IP address of the C2 server.",
                "  Using all these IOCs, they block the file, domain, and IP across",
                "  their entire infrastructure, stopping the attack chain."
            ]
        },
        {
            "id": "lesson_4",
            "title": "🎯 IOC CATEGORIES & CONFIDENCE LEVELS",
            "icon": "🎯",
            "color_scheme": 3,
            "content": [
                "Not all IOCs are created equal. Security teams categorize them",
                "based on confidence levels and threat intelligence:",
                "",
                "🟢 CATEGORY: CLEAN",
                "  • Confidence: 100%",
                "  • Action: Do not block",
                "  • Description: Confirmed safe, false positive",
                "  • Example: notepad.exe (legitimate Windows file)",
                "",
                "🟡 CATEGORY: SUSPICIOUS",
                "  • Confidence: 50-70%",
                "  • Action: Investigate",
                "  • Description: Potentially malicious, needs investigation",
                "  • Example: Unknown file in Temp folder",
                "",
                "🔴 CATEGORY: MALICIOUS",
                "  • Confidence: 80-100%",
                "  • Action: Block immediately",
                "  • Description: Confirmed malicious",
                "  • Example: Known ransomware hash",
                "",
                "📊 CONFIDENCE SCORING FACTORS:",
                "  • Multiple sources = Higher confidence",
                "  • Freshness = More recent = Higher confidence",
                "  • Source reliability = Trusted source = Higher confidence",
                "  • Context = Attack relevance = Higher confidence",
                "",
                "🎯 Real-World Scenario:",
                "  An analyst receives an alert about a suspicious file. The file hash",
                "  is flagged as malicious by 5 out of 70 antivirus engines (low",
                "  confidence). The analyst investigates further and finds the file",
                "  is actually a legitimate software update. They mark it as CLEAN.",
                "  Two weeks later, the same hash is flagged by 60 out of 70 engines",
                "  (high confidence) - the file was compromised after the update.",
                "  The analyst now blocks it immediately."
            ]
        },
        {
            "id": "lesson_5",
            "title": "🛡️ BEST PRACTICES FOR IOC MANAGEMENT",
            "icon": "🛡️",
            "color_scheme": 4,
            "content": [
                "Effective IOC management is crucial for a strong security posture:",
                "",
                "1. ALWAYS VALIDATE",
                "  • Cross-reference multiple sources",
                "  • Verify before blocking",
                "  • Consider false positives",
                "",
                "2. CONTEXT IS KEY",
                "  • Understand the attack scenario",
                "  • Know your environment",
                "  • Relevance matters",
                "",
                "3. TIMELINESS MATTERS",
                "  • Use fresh IOCs",
                "  • Remove outdated IOCs",
                "  • Regular updates",
                "",
                "4. SHARE RESPONSIBLY",
                "  • Protect sensitive information",
                "  • Use standard formats (STIX)",
                "  • Follow sharing protocols",
                "",
                "5. AUTOMATE WHERE POSSIBLE",
                "  • Auto-block known threats",
                "  • Auto-update IOC feeds",
                "  • Auto-generate alerts",
                "",
                "6. DOCUMENT EVERYTHING",
                "  • Source of IOC",
                "  • Discovery date",
                "  • Confidence level",
                "  • Related incidents",
                "",
                "🎯 Real-World Scenario:",
                "  A security team receives a new IOC feed from a trusted source.",
                "  Instead of blindly blocking all IOCs, they categorize them by",
                "  confidence level. Critical IOCs are automatically blocked.",
                "  Suspicious IOCs are sent to the SOC for manual review.",
                "  Clean IOCs are added to a whitelist. This approach prevents",
                "  false positives from disrupting business operations while",
                "  maintaining strong security."
            ]
        },
        {
            "id": "lesson_6",
            "title": "🔧 USING IOCS IN SOC LAB",
            "icon": "🔧",
            "color_scheme": 5,
            "content": [
                "The DSTerminal SOC Lab provides a complete IOC management system:",
                "",
                "STEP 1: Add an IOC",
                "  → Type: soc ioc",
                "  → Select type: hash, domain, ip, url, file, registry",
                "  → Enter value and categorize",
                "",
                "STEP 2: Test the IOC",
                "  → The lab will scan your system",
                "  → Find matching files, processes, or configurations",
                "",
                "STEP 3: View All IOCs",
                "  → See all loaded IOCs with categories and sources",
                "",
                "STEP 4: Monitor for IOC Matches",
                "  → Real-time file system monitoring",
                "  → Process behavior analysis",
                "",
                "STEP 5: Respond to IOC Matches",
                "  → Quarantine malicious files",
                "  → Block malicious domains and IPs",
                "  → Terminate malicious processes",
                "",
                "🎯 Real-World Scenario:",
                "  A SOC analyst discovers a new ransomware variant in the wild.",
                "  They extract the file hash, C2 domain, and IP address.",
                "  Using the SOC Lab, they add these as IOCs. The lab immediately",
                "  scans the entire network for matching files and processes.",
                "  It finds the ransomware on 3 endpoints that were missed by the",
                "  antivirus. The lab automatically quarantines the files and",
                "  blocks the C2 communication, stopping the attack in real-time."
            ]
        },
        {
            "id": "lesson_7",
            "title": "📚 IOC LEARNING RESOURCES",
            "icon": "📚",
            "color_scheme": 6,
            "content": [
                "Continue your IOC education with these resources:",
                "",
                "ONLINE PLATFORMS:",
                "  • VirusTotal: https://www.virustotal.com",
                "  • MISP: https://www.misp-project.org",
                "  • AlienVault OTX: https://otx.alienvault.com",
                "  • AbuseIPDB: https://www.abuseipdb.com",
                "",
                "THREAT INTELLIGENCE FEEDS:",
                "  • CISA Alerts: https://www.cisa.gov",
                "  • Talos Intelligence: https://talosintelligence.com",
                "  • SANS ISC: https://isc.sans.edu",
                "",
                "CERTIFICATIONS:",
                "  • CISSP - Certified Information Systems Security Professional",
                "  • CISA - Certified Information Systems Auditor",
                "  • CEH - Certified Ethical Hacker",
                "  • GIAC - Global Information Assurance Certification",
                "",
                "🎯 Real-World Scenario:",
                "  A junior security analyst wants to improve their IOC detection",
                "  skills. They start by using VirusTotal to research suspicious",
                "  hashes they encounter in their organization. They join the MISP",
                "  community and start sharing IOCs with other organizations.",
                "  They enroll in the CEH certification to learn more about",
                "  attacker techniques. Within 6 months, they've become the",
                "  organization's IOC expert, leading the threat hunting team."
            ]
        },
        {
            "id": "lesson_8",
            "title": "💡 WHY IOCS ARE CRITICAL FOR SECURITY",
            "icon": "💡",
            "color_scheme": 7,
            "content": [
                "IOCs are fundamental to modern cybersecurity operations:",
                "",
                "1. EARLY DETECTION",
                "  • Identify threats before they cause damage",
                "  • Reduce dwell time (time from compromise to detection)",
                "",
                "2. FAST RESPONSE",
                "  • Automated blocking of known threats",
                "  • Quick containment and remediation",
                "",
                "3. THREAT INTELLIGENCE",
                "  • Understand attacker TTPs (Tactics, Techniques, Procedures)",
                "  • Identify trends and patterns",
                "  • Stay ahead of emerging threats",
                "",
                "4. COMPLIANCE REQUIREMENTS",
                "  • GDPR (breach notification)",
                "  • HIPAA (patient data protection)",
                "  • PCI-DSS (cardholder data security)",
                "  • NIST CSF (cybersecurity framework)",
                "",
                "5. PROACTIVE HUNTING",
                "  • Search for threats proactively",
                "  • Find attackers before they strike",
                "  • Improve security posture",
                "",
                "6. ATTRIBUTION",
                "  • Identify threat actors",
                "  • Link attacks to known groups",
                "  • Understand motivations",
                "",
                "7. SHARING & COLLABORATION",
                "  • Share intelligence with others",
                "  • Benefit from community knowledge",
                "  • Contribute to global security",
                "",
                "🎯 Real-World Scenario:",
                "  A global organization implements a robust IOC program. Within the",
                "  first month, they detect a known APT group attempting to establish",
                "  persistence using a previously identified malware variant. The",
                "  IOCs immediately block the attempt, and the security team uses",
                "  the information to hunt for similar activity across the enterprise.",
                "  The organization shares the new IOCs with industry peers, helping",
                "  to prevent similar attacks across the sector. The quick detection",
                "  and response prevent a major data breach that would have cost",
                "  millions in fines and reputational damage."
            ]
        }
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
            sys.stdout.write(char)
            sys.stdout.flush()
            self.current_line_length += 1
            
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
        
        term = shutil.get_terminal_size((100, 30))
        
        if width is None:
            width = min(term.columns - 6, 110)
        
        width = max(width, 60)
        left_margin = max(0, (term.columns - width) // 2)
        inner = width - 4
        
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            wrapped.extend(
                textwrap.wrap(
                    line,
                    inner,
                    break_long_words=False,
                    replace_whitespace=False
                )
            )
        
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
            f"📚 Remaining: {remaining} lessons available",
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
        print(f"\n{Fore.CYAN}┌─ {Fore.YELLOW}Select option {Fore.CYAN}─►{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}[Y]{Style.RESET_ALL} Yes, show me another lesson")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}[N]{Style.RESET_ALL} No, I'm done for now")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}[L]{Style.RESET_ALL} List all available lessons")
        print(f"{Fore.CYAN}└─ {Fore.MAGENTA}Your choice {Fore.CYAN}►{Style.RESET_ALL} ", end="")
        
        choice = input().strip().lower()
        
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
        
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.LIGHTGREEN_EX}🛡️  INTERACTIVE IOC EDUCATION  {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Learn at your own pace{Fore.CYAN}  {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        time.sleep(0.5)
        
        while True:
            # Show a random lesson
            self.show_random_lesson(speed=pen_speed, auto_continue=False)
            
            # Ask if user wants to continue
            should_continue = self._show_continue_prompt(total_lessons, self.lessons_shown)
            
            if not should_continue:
                break
        
        # Farewell message
        os.system('cls' if os.name == 'nt' else 'clear')
        
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
        input()
    
    def show_random_lesson(self, speed: Optional[float] = None, auto_continue: bool = False):
        """
        Display a random IOC lesson with unique color scheme.
        Each run shows a different lesson.
        """
        pen_speed = speed if speed is not None else self.PEN_SPEED
        
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
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
            "  ██║  ██║██╔═══██╗██╔════╝██║ ██╔╝",
            "  ███████║██║   ██║██║     █████╔╝ ",
            "  ██╔══██║██║   ██║██║     ██╔═██╗ ",
            "  ██║  ██║╚██████╔╝╚██████╗██║  ██╗",
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
            f"📚 Lessons Completed: {self.lessons_shown}/{total_lessons}",
            f"📖 Remaining: {total_lessons - self.lessons_shown}",
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
            input()
    
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
    
    print(f"{Fore.CYAN}DSTerminal IOC Education Module v{IOCEducation.VERSION}{Style.RESET_ALL}")
    time.sleep(0.5)
    
    if args.list:
        print(f"\n{Fore.YELLOW}Available Lessons:{Style.RESET_ALL}")
        for i, lesson in enumerate(IOCEducation.IOC_LESSONS, 1):
            print(f"  {i}. {lesson['icon']} {lesson['title']}")
        print(f"\n{Fore.CYAN}Total: {len(IOCEducation.IOC_LESSONS)} lessons{Style.RESET_ALL}")
        return
    
    ioc = IOCEducation()
    
    if args.all:
        ioc.show_all_lessons(speed=args.speed)
    elif args.non_interactive:
        ioc.show_random_lesson(speed=args.speed)
    else:
        # Interactive mode with continue prompts
        ioc.run_interactive(speed=args.speed)


if __name__ == "__main__":
    main()