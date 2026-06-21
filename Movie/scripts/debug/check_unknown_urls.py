import csv

# Find all unknown files with their URLs
unknown_files = [
    "mJS0IF7Af3WpPRhSTDT6rGpiLzw",
    "MV5BYWIxNzdhNWQtNjAzYi00MTk4LTlmNTAtZDdiOGQ4ZWI0ZGU2XkEyXkFqcGc@",
]

with open('posters.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row.get('image_url', '')
        for unknown in unknown_files:
            if unknown in url:
                print(f"URL: {url}")
                print(f"File: {row.get('filename')}")
                print()
