import requests
import re
from pathlib import Path
from urllib.parse import urlparse
import os

def is_english(text):
    """Check if the text contains mostly English characters"""
    try:
        # Simple check for English characters and common symbols
        return bool(re.match(r'^[\x00-\x7F\s\-\'\"\(\)\[\]\{\}:;,!?]+$', text))
    except:
        return False

def filter_english_movies(input_url, output_file):
    try:
        # Fetch the M3U content
        response = requests.get(input_url, timeout=30)
        response.raise_for_status()
        
        lines = response.text.splitlines()
        filtered_lines = []
        current_entry = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF'):
                # If we have a complete entry, add it to filtered lines if it's English
                if current_entry and len(current_entry) >= 2 and is_english(current_entry[0]):
                    filtered_lines.extend(current_entry)
                current_entry = [line]
            elif current_entry:
                if len(current_entry) == 1:  # URL line
                    current_entry.append(line)
        
        # Add the last entry if it's English
        if current_entry and len(current_entry) >= 2 and is_english(current_entry[0]):
            filtered_lines.extend(current_entry)
        
        # Write the filtered M3U file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for i in range(0, len(filtered_lines), 2):
                if i + 1 < len(filtered_lines):
                    f.write(f"{filtered_lines[i]}\n{filtered_lines[i+1]}\n")
        
        print(f"Filtered M3U file created: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    INPUT_URL = "https://eviptv.com/m3u8/HasBahCa_MOVIES.m3u"
    OUTPUT_FILE = "english_movies.m3u"
    
    print(f"Filtering English movies from {INPUT_URL}")
    success = filter_english_movies(INPUT_URL, OUTPUT_FILE)
    
    if success:
        print("Processing completed successfully!")
    else:
        print("An error occurred during processing.")
        exit(1)
