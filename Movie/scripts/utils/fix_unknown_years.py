#!/usr/bin/env python
"""Find and help fix files without detected year."""

import os
import re
import csv
from pathlib import Path

OUTPUT_DIR = "posters"
CSV_FILE = "posters.csv"


def extract_year_from_filename(filename):
    """Extract year from filename."""
    match = re.search(r'_(\d{4})_', filename)
    if match:
        year = match.group(1)
        if 1895 <= int(year) <= 2030:
            return year
    return None


def extract_year_from_csv():
    """Get year from CSV."""
    year_map = {}
    if not os.path.exists(CSV_FILE):
        return year_map
    
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("filename"):
                    filename = row["filename"]
                    title = row.get("title", "")
                    
                    year = extract_year_from_filename(filename)
                    
                    if not year:
                        year_match = re.search(r'(\d{4})', title)
                        if year_match:
                            year = year_match.group(1)
                            if not (1895 <= int(year) <= 2030):
                                year = None
                    
                    if year:
                        year_map[filename] = year
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return year_map


def find_unknown_files():
    """Find files without year."""
    year_map = extract_year_from_csv()
    unknown = []
    
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.isdir(filepath):
            continue
        
        if os.path.isfile(filepath):
            year = year_map.get(filename)
            if not year:
                year = extract_year_from_filename(filename)
            
            if not year:
                unknown.append((filename, filepath))
    
    return unknown


def main():
    print("\n" + "=" * 70)
    print("🔍 Find Files Without Year")
    print("=" * 70)
    
    unknown = find_unknown_files()
    
    if not unknown:
        print("\n✅ All files have a detected year!")
        return
    
    print(f"\n❌ Found {len(unknown)} file(s) without detected year:\n")
    
    for i, (filename, filepath) in enumerate(unknown[:20], 1):
        size = os.path.getsize(filepath)
        print(f"{i:2d}. {filename}")
        print(f"    Size: {size:,} bytes")
        print()
    
    if len(unknown) > 20:
        print(f"... and {len(unknown) - 20} more files\n")
    
    # Suggestions
    print("=" * 70)
    print("💡 How to Fix:")
    print("=" * 70)
    print("""
Option 1: Edit CSV file (Recommended)
   • Open posters.csv with Excel/text editor
   • Find the filename in the "filename" column
   • Add year to the "title" column (e.g., "Movie Title 2023")

Option 2: Rename files manually
   • Add _YYYY_ pattern to filename
   • Example: title_2023_id.jpg
   
Option 3: Add to CSV directly
   • Add new rows with: page, title, image_url, filename
   • Include year in title field
   
Then run organize_by_year.py again!
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    main()
