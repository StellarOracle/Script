#!/usr/bin/env python
"""Organize remaining poster files by matching to CSV by page/index."""

import csv
import os
import re
import shutil

CSV_FILE = "posters.csv"
POSTERS_DIR = "posters"

def load_csv_data():
    """Load all CSV data into memory."""
    data = []
    if not os.path.exists(CSV_FILE):
        return data
    
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def get_year_from_title(title):
    """Extract year from title."""
    if not title:
        return None
    match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
    if match:
        return match.group(1)
    return None

def organize_remaining_files():
    """Organize files by finding them in CSV."""
    if not os.path.exists(POSTERS_DIR):
        print(f"❌ Directory not found: {POSTERS_DIR}")
        return
    
    csv_data = load_csv_data()
    print(f"Loaded {len(csv_data)} rows from CSV")
    
    # Create mapping: page -> list of (index, year, title)
    page_map = {}
    for row in csv_data:
        page = row.get('page', '')
        title = row.get('title', '')
        year = get_year_from_title(title)
        
        if page and year:
            if page not in page_map:
                page_map[page] = []
            page_map[page].append((title, year))
    
    moved = 0
    skipped = 0
    unknown = 0
    
    # Process files in root directory
    for filename in os.listdir(POSTERS_DIR):
        file_path = os.path.join(POSTERS_DIR, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Skip if not image
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue
        
        # Parse filename format: PAGE_INDEX_TITLE_...
        match = re.match(r'(\d{3})_(\d{3})_', filename)
        if not match:
            skipped += 1
            continue
        
        page = match.group(1)
        index = match.group(2)
        
        # Try to find year from page
        year = None
        if page in page_map and len(page_map[page]) > int(index) - 1:
            _, year = page_map[page][int(index) - 1]
        
        if not year:
            unknown += 1
            continue
        
        # Create year directory and move file
        year_dir = os.path.join(POSTERS_DIR, year)
        os.makedirs(year_dir, exist_ok=True)
        
        dest_path = os.path.join(year_dir, filename)
        
        # Skip if already there
        if os.path.exists(dest_path):
            skipped += 1
            continue
        
        try:
            shutil.move(file_path, dest_path)
            moved += 1
            if moved % 100 == 0:
                print(f"  ✓ Moved {moved} files...")
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Moved: {moved}")
    print(f"⏭️  Already organized: {skipped}")
    print(f"❓ No year found: {unknown}")
    print("="*60)

if __name__ == "__main__":
    organize_remaining_files()
