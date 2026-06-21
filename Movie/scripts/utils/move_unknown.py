#!/usr/bin/env python
"""Move remaining files to 'unknown' folder."""

import os
import shutil

POSTERS_DIR = "posters"

def move_unknown_files():
    """Move all remaining files to unknown folder."""
    if not os.path.exists(POSTERS_DIR):
        print(f"❌ Directory not found: {POSTERS_DIR}")
        return
    
    unknown_dir = os.path.join(POSTERS_DIR, "unknown")
    os.makedirs(unknown_dir, exist_ok=True)
    
    moved = 0
    skipped = 0
    
    # Process files in root directory
    for filename in os.listdir(POSTERS_DIR):
        file_path = os.path.join(POSTERS_DIR, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Skip if not image
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue
        
        dest_path = os.path.join(unknown_dir, filename)
        
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
    print(f"✅ Moved to 'unknown' folder: {moved}")
    print(f"⏭️  Already there: {skipped}")
    print("="*60)

if __name__ == "__main__":
    move_unknown_files()
