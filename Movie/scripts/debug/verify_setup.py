#!/usr/bin/env python
"""Quick test to verify the setup and show what was changed."""

import os
import csv
from pathlib import Path

OUTPUT_DIR = "posters"
CSV_FILE = "posters.csv"


def check_setup():
    """Verify the setup and show statistics."""
    print("\n" + "=" * 60)
    print("🎬 MOVIE POSTER TOOL - VERIFICATION")
    print("=" * 60)
    
    # Check directory
    if not os.path.exists(OUTPUT_DIR):
        print(f"\n✗ {OUTPUT_DIR} folder not found!")
        return False
    
    print(f"\n✓ {OUTPUT_DIR} folder exists")
    
    # Count files
    files = [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
    folders = [f for f in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, f))]
    
    total_files = files + sum([len(os.listdir(os.path.join(OUTPUT_DIR, f))) for f in folders])
    
    print(f"\n📊 Statistics:")
    print(f"   • Files in root: {len(files)}")
    print(f"   • Year folders: {len(folders)}")
    if folders:
        print(f"   • Year folders: {', '.join(sorted(folders))}")
    print(f"   • Total files: {total_files}")
    
    # Check CSV
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"\n📝 CSV Metadata:")
                print(f"   • Records: {len(rows)}")
                if rows:
                    print(f"   • First: {rows[0].get('title', 'N/A')}")
                    print(f"   • Last: {rows[-1].get('title', 'N/A')}")
        except Exception as e:
            print(f"\n✗ Error reading CSV: {e}")
    else:
        print(f"\n⚠ {CSV_FILE} not found")
    
    # Show what changed
    print(f"\n✨ What's New:")
    print(f"   ✓ download_posters.py - now checks for existing files")
    print(f"   ✓ organize_by_year.py - organize & remove duplicates")
    print(f"   ✓ README.md - documentation in Persian & English")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Run: python download_posters.py --start-page 184 --append")
    print(f"   2. Run: python organize_by_year.py")
    
    print("\n" + "=" * 60)
    return True


if __name__ == "__main__":
    check_setup()
