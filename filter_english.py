import re
import requests
from langdetect import detect, LangDetectException
import sys

# Source playlist URL
SOURCE_URL = "https://evdestek.ch/m3u8/HasBahCa_MOVIES.m3u"
OUTPUT_FILE = "english_movies.m3u"

def is_likely_english(title):
    """
    Heuristic + langdetect to determine if title is English.
    - First: quick ASCII check (excludes Cyrillic, Arabic, etc.)
    - Then: langdetect for more precision
    """
    if not title:
        return False
    
    # Quick filter: mostly basic Latin chars (allows accents like é, ñ but excludes non-Latin scripts)
    if not re.match(r'^[\x00-\x7F\u00C0-\u017F\s\!\?\.,:;\'"\-()&]+$', title):
        return False  # Has non-Latin characters → probably not English
    
    # Common English title patterns (boosts accuracy for short titles)
    english_indicators = ['the ', ' a ', ' an ', ' of ', ' in ', ' to ', ' and ', ' by ', ' from ', ' with ']
    if any(ind in title.lower() for ind in english_indicators):
        return True
    
    # langdetect fallback
    try:
        lang = detect(title)
        return lang == 'en'
    except LangDetectException:
        # If detection fails (short title, etc.), trust the ASCII + indicators check
        return ' (' in title or title.strip().isdigit() == False  # e.g. has year (2023)

def filter_m3u():
    print("Downloading source M3U...")
    try:
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to download: {e}")
        sys.exit(1)
    
    lines = response.text.splitlines()
    filtered_lines = []
    current_entry = []
    kept = 0
    total = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        if line.startswith("#EXTINF:"):
            current_entry = [line]
            # Try to extract title
            title = ""
            title_match = re.search(r'tvg-name="([^"]+)"', line)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # Fallback: after the last comma
                comma_parts = line.split(',', 1)
                if len(comma_parts) > 1:
                    title = comma_parts[1].strip()
            
            if title and is_likely_english(title):
                kept += 1
                filtered_lines.extend(current_entry)
                # Append the URL and any following lines until next EXTINF
                i += 1
                while i < len(lines) and not lines[i].startswith("#EXTINF:"):
                    filtered_lines.append(lines[i].rstrip())
                    i += 1
                continue
            else:
                total += 1
        else:
            if current_entry:
                current_entry.append(line)
        
        i += 1
    
    # Add header if present
    if lines and lines[0].startswith("#EXTM3U"):
        filtered_lines.insert(0, lines[0])
    
    print(f"Processed {total + kept} entries → kept {kept} likely English")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines) + "\n")
    
    print(f"Saved filtered playlist to {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_m3u()
