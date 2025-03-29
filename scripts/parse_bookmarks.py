#!/usr/bin/env python3
import json
import sys
from bs4 import BeautifulSoup

def parse_bookmarks(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    bookmarks = {}
    
    def process_folder(folder):
        result = {
            'title': folder.get('title', ''),
            'items': []
        }
        
        for item in folder.find_all(['a', 'h3', 'dl'], recursive=False):
            if item.name == 'a':
                result['items'].append({
                    'title': item.string,
                    'url': item.get('href', ''),
                    'icon': '🔖'
                })
            elif item.name == 'dl':
                subfolder = process_folder(item)
                if subfolder['items']:
                    result['items'].append(subfolder)
        
        return result
    
    for folder in soup.find_all('dl'):
        if folder.parent.name != 'dl':
            category = process_folder(folder)
            if category['items']:
                bookmarks[category['title']] = category['items']
    
    return bookmarks

def save_bookmarks(bookmarks, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python parse_bookmarks.py <input_html> <output_json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    bookmarks = parse_bookmarks(input_file)
    save_bookmarks(bookmarks, output_file) 