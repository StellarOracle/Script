#!/usr/bin/env python
"""One-command solution: Download, organize, and clean up.

Usage:
    python run_all.py              # Interactive mode
    python run_all.py --download   # Download only
    python run_all.py --organize   # Organize only
    python run_all.py --both       # Download then organize
"""

import subprocess
import sys
import argparse


def run_download(start_page=184, end_page=None):
    """Run download script."""
    print("\n" + "=" * 60)
    print("📥 Starting download...")
    print("=" * 60)
    
    cmd = ["python", "download_posters.py", f"--start-page", str(start_page), "--append"]
    if end_page:
        cmd.extend(["--end-page", str(end_page)])
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_organize():
    """Run organization script."""
    print("\n" + "=" * 60)
    print("🗂️ Starting organization & cleanup...")
    print("=" * 60)
    
    cmd = ["python", "organize_by_year.py"]
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Download, organize and clean up movie posters"
    )
    parser.add_argument("--download", action="store_true", help="Download only")
    parser.add_argument("--organize", action="store_true", help="Organize only")
    parser.add_argument("--both", action="store_true", help="Download then organize")
    parser.add_argument("--start-page", type=int, default=184, help="Start page")
    parser.add_argument("--end-page", type=int, default=None, help="End page")
    
    args = parser.parse_args()
    
    # Determine mode
    if not any([args.download, args.organize, args.both]):
        # Interactive mode
        print("\n" + "=" * 60)
        print("🎬 MOVIE POSTER TOOL")
        print("=" * 60)
        print("\nWhat would you like to do?")
        print("  1. Download new posters")
        print("  2. Organize & clean up")
        print("  3. Do both (download then organize)")
        print("  4. Exit")
        
        choice = input("\nChoose (1-4): ").strip()
        
        if choice == "1":
            run_download(args.start_page, args.end_page)
        elif choice == "2":
            run_organize()
        elif choice == "3":
            if run_download(args.start_page, args.end_page):
                run_organize()
        else:
            print("Exiting...")
    else:
        # Command line mode
        if args.download:
            run_download(args.start_page, args.end_page)
        elif args.organize:
            run_organize()
        elif args.both:
            if run_download(args.start_page, args.end_page):
                run_organize()
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
