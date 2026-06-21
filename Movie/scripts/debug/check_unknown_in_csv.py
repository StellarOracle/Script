#!/usr/bin/env python
"""Check all unknown files against CSV."""

import csv
import os

CSV_FILE = "posters.csv"
POSTERS_DIR = "posters"
UNKNOWN_DIR = os.path.join(POSTERS_DIR, "unknown")

# Load all CSV filenames
csv_filenames = set()
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_filenames.add(row.get('filename', ''))

print(f"CSV has {len(csv_filenames)} filenames")

# Check unknown files
unknown_files = []
for filename in os.listdir(UNKNOWN_DIR):
    file_path = os.path.join(UNKNOWN_DIR, filename)
    if os.path.isfile(file_path):
        unknown_files.append(filename)

print(f"Unknown folder has {len(unknown_files)} files")

# Check if any unknown files are in CSV
found_in_csv = 0
not_in_csv = 0

for filename in unknown_files[:20]:
    if filename in csv_filenames:
        found_in_csv += 1
        print(f"✓ {filename[:50]}")
    else:
        not_in_csv += 1
        print(f"✗ {filename[:50]} - NOT IN CSV")

print(f"\nSummary of first 20:")
print(f"  Found in CSV: {found_in_csv}")
print(f"  NOT in CSV: {not_in_csv}")
