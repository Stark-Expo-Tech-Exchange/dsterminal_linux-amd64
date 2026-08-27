#!python
# ============================================================
# FIX UNICODE ENCODING ISSUES FOR WINDOWS CONSOLE
# ============================================================
import sys
import io
import os

# Safe stdout/stderr handling for GUI executables
if sys.platform == 'win32':
    try:
        # Set console code page to UTF-8 (only if console exists)
        if sys.stdout is not None:
            os.system('chcp 65001 > nul')
    except:
        pass
    
    # Replace stdout/stderr with UTF-8 wrappers (only if they exist)
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        except:
            pass
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
        except:
            pass

def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        # Check if stdout exists before printing
        if sys.stdout is not None:
            print(message)
        # If stdout is None (windowed mode), log to file instead
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
            except:
                pass
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        if sys.stdout is not None:
            print(clean_message)
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(clean_message + '\n')
            except:
                pass
    except:
        pass  # Silent fail for GUI mode

import requests

username = "Stark-Expo-Tech-Exchange"
url = f"https://api.github.com/users/{username}/repos"

print(f"Checking repositories for: {username}")
print("=" * 50)

try:
    response = requests.get(url, headers={'User-Agent': 'DSTerminal-Test'})
    
    if response.status_code == 200:
        repos = response.json()
        print(f"âœ… Found {len(repos)} public repository(ies)\n")
        
        for repo in repos:
            name = repo.get('name')
            private = repo.get('private', False)
            visibility = "ðŸ”’ Private" if private else "ðŸŒ Public"
            default_branch = repo.get('default_branch', 'main')
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            
            print(f"ðŸ“ {name}")
            print(f"   Visibility: {visibility}")
            print(f"   Default branch: {default_branch}")
            print(f"   â­ {stars} | ðŸ´ {forks}")
            
            # Check if it has releases
            releases_url = f"https://api.github.com/repos/{username}/{name}/releases"
            releases_response = requests.get(releases_url, headers={'User-Agent': 'DSTerminal-Test'})
            if releases_response.status_code == 200:
                releases = releases_response.json()
                if releases:
                    print(f"   ðŸ“¦ Releases: {len(releases)} (latest: {releases[0].get('tag_name', 'Unknown')})")
                else:
                    print(f"   ðŸ“¦ No releases")
            print()
    elif response.status_code == 404:
        print(f"âŒ User '{username}' not found")
    else:
        print(f"âŒ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"âŒ Error: {e}")