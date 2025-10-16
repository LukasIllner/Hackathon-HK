#!/usr/bin/env python3
"""
Parse api.txt and create api_links.csv
"""
import csv
from pathlib import Path

def parse_api_txt(filepath):
    """Parse api.txt file and extract category names and URLs"""
    api_data = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_category = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and separator lines
        if not line or line.startswith('_____'):
            continue
        
        # If line starts with http, it's a URL for the previous category
        if line.startswith('http'):
            if current_category:
                api_data.append({
                    'category': current_category,
                    'api_url': line
                })
                current_category = None
        else:
            # It's a category name
            current_category = line
    
    return api_data

def write_csv(data, output_path):
    """Write data to CSV file"""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['category', 'api_url'])
        writer.writeheader()
        writer.writerows(data)

def main():
    # Path to api.txt (in parent directory)
    api_txt_path = Path(__file__).parent.parent / 'api.txt'
    
    # Output CSV path
    csv_output_path = Path(__file__).parent / 'api_links.csv'
    
    print("=" * 60)
    print("Parsing api.txt to create api_links.csv")
    print("=" * 60)
    
    # Parse the file
    print(f"\n📖 Reading: {api_txt_path}")
    api_data = parse_api_txt(api_txt_path)
    
    print(f"✅ Found {len(api_data)} API endpoints\n")
    
    # Display the data
    print("Categories found:")
    for i, item in enumerate(api_data, 1):
        print(f"  {i}. {item['category']}")
    
    # Write to CSV
    print(f"\n💾 Writing to: {csv_output_path}")
    write_csv(api_data, csv_output_path)
    
    print("✅ CSV file created successfully!")
    print(f"\nOutput: {csv_output_path}")
    print(f"Total entries: {len(api_data)}")

if __name__ == "__main__":
    main()
