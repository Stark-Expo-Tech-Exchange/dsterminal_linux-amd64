# clean_unicode.py - Run this on your dsterminal_complete.py
import re

with open('dsterminal_complete.py', 'r', encoding='utf-8') as f:
    content = f.read()


# Replace common emojis
replacements = {
    '✅': '[OK]',
    '🔴': '[ERROR]',
    '🟢': '[SUCCESS]',
    '🟡': '[INFO]',
    '⚠️': '[WARNING]',
    '📁': '[FOLDER]',
    '🔒': '[LOCK]',
    '🔓': '[UNLOCK]',
    '🤖': '[BOT]',
    '🚨': '[ALERT]',
    '📊': '[CHART]',
    '📈': '[CHART]',
    '💡': '[TIP]',
    '📋': '[LIST]',
    '📄': '[DOC]',
    '🔍': '[SEARCH]',
    '⚡': '[POWER]',
}

for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

with open('dsterminal_complete_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("File cleaned!")