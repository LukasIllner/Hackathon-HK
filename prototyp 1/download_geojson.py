#!/usr/bin/env python3
"""
Download all GeoJSON files from API links
"""
import csv
import json
import os
import requests
from pathlib import Path
import time

def sanitize_filename(name):
    """Create a safe filename from category name"""
    # Remove special characters and replace spaces with underscores
    safe_name = name.replace('/', '_').replace('\\', '_')
    safe_name = safe_name.replace(':', '_').replace('*', '_')
    safe_name = safe_name.replace('?', '_').replace('"', '_')
    safe_name = safe_name.replace('<', '_').replace('>', '_')
    safe_name = safe_name.replace('|', '_')
    return safe_name

def download_geojson(url, category, output_dir):
    """Download GeoJSON from URL and save to file"""
    try:
        print(f"Downloading: {category}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse JSON to validate
        geojson_data = response.json()
        
        # Create filename from category
        filename = sanitize_filename(category) + '.geojson'
        filepath = output_dir / filename
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)
        
        feature_count = len(geojson_data.get('features', []))
        print(f"  ✓ Saved {filename} ({feature_count} features)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error downloading {category}: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"  ✗ Error parsing JSON for {category}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error for {category}: {e}")
        return False

def main():
    # Define paths
    base_path = Path(__file__).parent
    csv_file = base_path / 'api_links.csv'
    output_dir = base_path / 'data HK - rande geojson'
    
    # Also create in parent directory (Hackathon HK)
    parent_output_dir = base_path.parent / 'data HK - rande geojson'
    
    print("=" * 60)
    print("GeoJSON Download Script - Hackathon HK")
    print("=" * 60)
    
    # Check if CSV file exists
    if not csv_file.exists():
        print(f"ERROR: {csv_file} not found!")
        return
    
    # Create output directories
    output_dir.mkdir(exist_ok=True)
    print(f"\n✓ Created directory: {output_dir}")
    
    parent_output_dir.mkdir(exist_ok=True)
    print(f"✓ Created directory: {parent_output_dir}")
    
    # Clear existing files to avoid duplicates
    print("\nClearing existing files...")
    for filepath in output_dir.glob('*.geojson'):
        filepath.unlink()
        print(f"  Deleted: {filepath.name}")
    
    for filepath in parent_output_dir.glob('*.geojson'):
        filepath.unlink()
        print(f"  Deleted: {filepath.name}")
    
    # Read CSV and download files
    print("\nDownloading GeoJSON files...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            category = row.get('category', '').strip()
            api_url = row.get('api_url', '').strip()
            
            if not category or not api_url:
                continue
            
            # Download to prototyp 1 directory (primary)
            if download_geojson(api_url, category, output_dir):
                successful += 1
                
                # Copy to parent directory (Hackathon HK)
                filename = sanitize_filename(category) + '.geojson'
                src_file = output_dir / filename
                dst_file = parent_output_dir / filename
                
                # Copy file
                import shutil
                shutil.copy2(src_file, dst_file)
                print(f"  ✓ Copied to parent directory")
            else:
                failed += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("Download Summary:")
    print("=" * 60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")
    print(f"\nFiles saved to:")
    print(f"  1. {output_dir}")
    print(f"  2. {parent_output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
