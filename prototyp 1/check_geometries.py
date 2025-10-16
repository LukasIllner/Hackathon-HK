#!/usr/bin/env python3
"""
Check which GeoJSON files contain polygon geometries
"""
import json
from pathlib import Path

def check_geojson_geometries(directory_path):
    """Check geometry types in all GeoJSON files"""
    directory = Path(directory_path)
    
    files_with_polygons = []
    files_without_polygons = []
    
    for filepath in directory.glob('*.geojson'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            has_polygon = False
            geometry_types = set()
            
            if data.get('type') == 'FeatureCollection':
                for feature in data.get('features', []):
                    geom_type = feature.get('geometry', {}).get('type', '')
                    geometry_types.add(geom_type)
                    
                    if 'Polygon' in geom_type:  # Matches "Polygon" and "MultiPolygon"
                        has_polygon = True
            
            if has_polygon:
                files_with_polygons.append({
                    'file': filepath.name,
                    'types': geometry_types
                })
            else:
                files_without_polygons.append({
                    'file': filepath.name,
                    'types': geometry_types
                })
                
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")
    
    return files_with_polygons, files_without_polygons

def main():
    base_path = Path(__file__).parent
    data_dir = base_path / 'data HK - rande geojson'
    
    print("=" * 60)
    print("GeoJSON Geometry Type Checker")
    print("=" * 60)
    
    files_with_polygons, files_without_polygons = check_geojson_geometries(data_dir)
    
    print(f"\nFiles WITH Polygon geometries ({len(files_with_polygons)}):")
    print("-" * 60)
    for item in files_with_polygons:
        print(f"  - {item['file']}")
        print(f"    Geometry types: {', '.join(item['types'])}")
    
    print(f"\nFiles WITHOUT Polygon geometries ({len(files_without_polygons)}):")
    print("-" * 60)
    for item in files_without_polygons:
        print(f"  - {item['file']}")
        print(f"    Geometry types: {', '.join(item['types'])}")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Files with polygons: {len(files_with_polygons)}")
    print(f"  Files without polygons: {len(files_without_polygons)}")
    print(f"  Total: {len(files_with_polygons) + len(files_without_polygons)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
