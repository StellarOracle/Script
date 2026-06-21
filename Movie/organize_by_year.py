#!/usr/bin/env python
"""Organize downloaded posters by year into separate folders.

Usage:
    python organize_by_year.py

This script:
1. Extracts the year from the filename or CSV metadata
2. Creates year-based folders
3. Moves files to their corresponding year folders
4. Removes duplicate files (based on content hash)
"""

import os
import re
import csv
import hashlib
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = "posters"
CSV_FILE = "posters.csv"


def get_file_hash(filepath):
    """Get MD5 hash of a file to detect duplicates."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_year_from_filename(filename):
    """Extract year from filename."""
    # Pattern: Year appears as 4 digits within the filename
    # Example: دانلود_فیلم_Poor_Things_2023_...jpg
    match = re.search(r'_(\d{4})_', filename)
    if match:
        year = match.group(1)
        # Validate it's a reasonable year (between 1895 and current year + 1)
        if 1895 <= int(year) <= 2030:
            return year
    return None


def extract_year_from_csv():
    """Extract years from CSV file for mapping."""
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
                    
                    # Try to extract year from filename first
                    year = extract_year_from_filename(filename)
                    
                    # If not found, try to extract from title
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


def find_duplicates():
    """Find duplicate files based on content hash."""
    if not os.path.exists(OUTPUT_DIR):
        return {}
    
    hash_map = defaultdict(list)
    
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.isfile(filepath):
            try:
                file_hash = get_file_hash(filepath)
                hash_map[file_hash].append(filename)
            except Exception as e:
                print(f"Error hashing {filename}: {e}")
    
    # Return only hashes with duplicates
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    return duplicates


def remove_duplicates(keep_newest=True):
    """Remove duplicate files, keeping only one copy."""
    duplicates = find_duplicates()
    
    if not duplicates:
        print("✓ No duplicate files found")
        return 0
    
    removed_count = 0
    for file_hash, filenames in duplicates.items():
        print(f"\n Found duplicates (hash: {file_hash[:8]}...):")
        for fname in filenames:
            print(f"  - {fname}")
        
        # Keep the first one, remove the rest
        if keep_newest:
            # Sort by modification time, keep newest
            files_with_time = [
                (f, os.path.getmtime(os.path.join(OUTPUT_DIR, f)))
                for f in filenames
            ]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            to_keep = files_with_time[0][0]
            to_remove = [f[0] for f in files_with_time[1:]]
        else:
            to_keep = filenames[0]
            to_remove = filenames[1:]
        
        print(f"  Keeping: {to_keep}")
        
        for fname in to_remove:
            filepath = os.path.join(OUTPUT_DIR, fname)
            try:
                os.remove(filepath)
                print(f"  ✓ Removed: {fname}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Error removing {fname}: {e}")
    
    return removed_count


def organize_by_year():
    """Organize files into year-based folders."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: {OUTPUT_DIR} folder does not exist")
        return 0
    
    year_map = extract_year_from_csv()
    organized_count = 0
    unknown_files = []
    
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Skip if it's a folder
        if os.path.isdir(filepath):
            continue
        
        # Get year from mapping or filename
        year = year_map.get(filename)
        if not year:
            year = extract_year_from_filename(filename)
        
        if year:
            year_folder = os.path.join(OUTPUT_DIR, year)
            
            # Create year folder if it doesn't exist
            os.makedirs(year_folder, exist_ok=True)
            
            # Move file to year folder
            new_filepath = os.path.join(year_folder, filename)
            
            try:
                os.rename(filepath, new_filepath)
                print(f"  ✓ {filename} -> {year}/")
                organized_count += 1
            except Exception as e:
                print(f"  ✗ Error moving {filename}: {e}")
        else:
            # Track files without year
            unknown_files.append(filename)
    
    # Show files without year
    if unknown_files:
        print(f"\n⚠️  {len(unknown_files)} file(s) without year detected:")
        for fname in unknown_files[:10]:  # Show first 10
            print(f"   - {fname}")
        if len(unknown_files) > 10:
            print(f"   ... and {len(unknown_files) - 10} more")
        print("\n💡 Tip: Edit the filename or CSV to include year (format: _YYYY_)")
    
    return organized_count


def main():
    print("=" * 60)
    print("Movie Poster Organization Tool")
    print("=" * 60)
    
    # Step 1: Remove duplicates
    print("\n[1/2] Detecting and removing duplicate files...")
    print("-" * 60)
    removed = remove_duplicates()
    print(f"\n✓ Removed {removed} duplicate file(s)")
    
    # Step 2: Organize by year
    print("\n[2/2] Organizing files by year...")
    print("-" * 60)
    organized = organize_by_year()
    print(f"\n✓ Organized {organized} file(s) into year folders")
    
    print("\n" + "=" * 60)
    print("Done! Your posters are now organized by year.")
    print("=" * 60)


if __name__ == "__main__":
    main()
