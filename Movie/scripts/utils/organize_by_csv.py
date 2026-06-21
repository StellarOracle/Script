#!/usr/bin/env python
"""Better poster organization using direct file scanning."""

import csv
import os
import shutil
import re
from pathlib import Path

CSV_FILE = "posters.csv"
POSTERS_DIR = "posters"

def load_csv_mapping():
    """Load filename to year mapping from CSV."""
    mapping = {}
    if not os.path.exists(CSV_FILE):
        return mapping
    
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get('filename', '')
            title = row.get('title', '')
            
            if not filename or not title:
                continue
            
            # Extract year from title (e.g., "Movie Title 2006 ...")
            year = None
            match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
            if match:
                year = match.group(1)
            
            if year:
                mapping[filename] = year
    
    return mapping

def organize_posters():
    """Scan posters directory and organize by year."""
    if not os.path.exists(POSTERS_DIR):
        print(f"❌ Directory not found: {POSTERS_DIR}")
        return
    
    mapping = load_csv_mapping()
    print(f"Loaded mapping for {len(mapping)} files from CSV\n")
    
    moved = 0
    skipped = 0
    no_year = 0
    
    # Scan root posters directory
    for filename in os.listdir(POSTERS_DIR):
        file_path = os.path.join(POSTERS_DIR, filename)
        
        # Skip if it's a directory
        if os.path.isdir(file_path):
            continue
        
        # Skip if not an image
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue
        
        # Try to get year from mapping
        year = mapping.get(filename)
        
        if not year:
            no_year += 1
            continue
        
        # Create year directory
        year_dir = os.path.join(POSTERS_DIR, year)
        os.makedirs(year_dir, exist_ok=True)
        
        dest_path = os.path.join(year_dir, filename)
        
        # Skip if already in place
        if os.path.exists(dest_path):
            skipped += 1
            continue
        
        # Move file
        shutil.move(file_path, dest_path)
        moved += 1
        
        if moved % 100 == 0:
            print(f"  ✓ Moved {moved} files...")
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Moved: {moved}")
    print(f"⏭️  Already organized: {skipped}")
    print(f"⚠️  No year in CSV: {no_year}")
    print("="*60)

if __name__ == "__main__":
    organize_posters()
