#!/usr/bin/env python
"""Extract year from image URLs and reorganize unknown files."""

import csv
import os
import re
import shutil

CSV_FILE = "posters.csv"
POSTERS_DIR = "posters"

def extract_year_from_url(url):
    """Extract year from URL path (e.g., /2018/05/ -> 2018)."""
    if not url:
        return None
    
    # Look for /YYYY/ pattern in URL
    match = re.search(r'/(\d{4})/', url)
    if match:
        year = match.group(1)
        # Verify it's a reasonable year
        if 1900 <= int(year) <= 2099:
            return year
    
    return None

def reorganize_unknown_files():
    """Move unknown files to correct year folders based on URL."""
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found: {CSV_FILE}")
        return
    
    if not os.path.exists(POSTERS_DIR):
        print(f"❌ Directory not found: {POSTERS_DIR}")
        return
    
    # Load CSV and create mapping: filename -> year
    filename_to_year = {}
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get('filename', '')
            url = row.get('image_url', '')
            
            if filename and url:
                year = extract_year_from_url(url)
                if year:
                    filename_to_year[filename] = year
    
    print(f"Loaded URL→year mapping for {len(filename_to_year)} files")
    
    unknown_dir = os.path.join(POSTERS_DIR, "unknown")
    if not os.path.exists(unknown_dir):
        print(f"⚠️  No 'unknown' folder found")
        return
    
    moved = 0
    already_correct = 0
    no_year_found = 0
    
    # Process files in unknown folder
    for filename in os.listdir(unknown_dir):
        file_path = os.path.join(unknown_dir, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Skip if not image
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue
        
        # Get year from mapping
        year = filename_to_year.get(filename)
        
        if not year:
            no_year_found += 1
            continue
        
        # Create year directory
        year_dir = os.path.join(POSTERS_DIR, year)
        os.makedirs(year_dir, exist_ok=True)
        
        dest_path = os.path.join(year_dir, filename)
        
        # Skip if already there
        if os.path.exists(dest_path):
            already_correct += 1
            continue
        
        try:
            shutil.move(file_path, dest_path)
            moved += 1
            if moved % 50 == 0:
                print(f"  ✓ Moved {moved} files...")
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Moved to correct year: {moved}")
    print(f"ℹ️  Already correct: {already_correct}")
    print(f"❌ No year in URL: {no_year_found}")
    print("="*60)

if __name__ == "__main__":
    reorganize_unknown_files()
