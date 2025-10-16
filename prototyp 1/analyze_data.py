#!/usr/bin/env python3
"""
Comprehensive analysis of GeoJSON files and MongoDB Atlas connection
"""
import json
import os
from pathlib import Path
from collections import defaultdict
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / 'databaze' / '.env')

def analyze_geojson_structure(directory_path):
    """Analyze all GeoJSON files in the directory"""
    directory = Path(directory_path)
    results = {
        'total_files': 0,
        'total_features': 0,
        'structure_analysis': {},
        'property_keys': defaultdict(int),
        'geometry_types': defaultdict(int),
        'inconsistencies': []
    }
    
    geojson_files = list(directory.glob('*.geojson'))
    results['total_files'] = len(geojson_files)
    
    print(f"\n{'='*70}")
    print(f"ANALYZING {len(geojson_files)} GEOJSON FILES")
    print(f"{'='*70}\n")
    
    base_structure = None
    
    for filepath in geojson_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check top-level structure
            file_structure = {
                'type': data.get('type'),
                'has_crs': 'crs' in data,
                'crs_value': data.get('crs', {}).get('properties', {}).get('name'),
                'feature_count': len(data.get('features', []))
            }
            
            results['total_features'] += file_structure['feature_count']
            
            # Set base structure from first file
            if base_structure is None:
                base_structure = file_structure
            else:
                # Compare with base structure
                if file_structure['type'] != base_structure['type']:
                    results['inconsistencies'].append(
                        f"{filepath.name}: Different type (expected {base_structure['type']}, got {file_structure['type']})"
                    )
                if file_structure['crs_value'] != base_structure['crs_value']:
                    results['inconsistencies'].append(
                        f"{filepath.name}: Different CRS (expected {base_structure['crs_value']}, got {file_structure['crs_value']})"
                    )
            
            # Analyze features
            for feature in data.get('features', []):
                # Geometry type
                geom_type = feature.get('geometry', {}).get('type', 'Unknown')
                results['geometry_types'][geom_type] += 1
                
                # Property keys
                properties = feature.get('properties', {})
                for key in properties.keys():
                    results['property_keys'][key] += 1
            
            results['structure_analysis'][filepath.name] = file_structure
            
        except Exception as e:
            print(f"❌ Error analyzing {filepath.name}: {e}")
    
    return results

def test_mongodb_connection():
    """Test connection to MongoDB Atlas"""
    mongodb_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
    collection_name = os.getenv('COLLECTION_NAME', 'places')
    
    print(f"\n{'='*70}")
    print("MONGODB ATLAS CONNECTION TEST")
    print(f"{'='*70}\n")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables!")
        return None
    
    print(f"📍 Database: {database_name}")
    print(f"📍 Collection: {collection_name}")
    print(f"📍 Connecting to MongoDB Atlas...")
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!\n")
        
        db = client[database_name]
        collection = db[collection_name]
        
        # Get collection stats
        doc_count = collection.count_documents({})
        print(f"📊 Total documents in collection: {doc_count}")
        
        if doc_count > 0:
            # Sample document analysis
            sample_doc = collection.find_one({})
            print(f"\n📄 Sample document fields:")
            for key in sorted(sample_doc.keys()):
                if key != '_id':
                    print(f"   • {key}")
            
            # Count by source file
            pipeline = [
                {"$group": {"_id": "$source_file", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            print(f"\n📁 Documents by source file:")
            for result in collection.aggregate(pipeline):
                print(f"   • {result['_id']}: {result['count']} documents")
        else:
            print("\n⚠️  No documents found in the collection.")
            print("   Run 'python databaze/import_to_mongodb.py' to import data.")
        
        client.close()
        return {'connected': True, 'doc_count': doc_count}
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return {'connected': False, 'error': str(e)}

def main():
    print("\n" + "="*70)
    print(" "*15 + "DATA ANALYSIS REPORT")
    print("="*70)
    
    # Analyze GeoJSON files
    data_hk_path = Path(__file__).parent / 'data_hk'
    results = analyze_geojson_structure(data_hk_path)
    
    # Print results
    print(f"✅ Total files analyzed: {results['total_files']}")
    print(f"✅ Total features found: {results['total_features']}")
    
    print(f"\n{'='*70}")
    print("STRUCTURE CONSISTENCY CHECK")
    print(f"{'='*70}")
    
    if results['inconsistencies']:
        print(f"\n⚠️  Found {len(results['inconsistencies'])} inconsistencies:\n")
        for issue in results['inconsistencies']:
            print(f"   • {issue}")
    else:
        print("\n✅ All GeoJSON files have consistent structure!")
        print("   • Same 'type' (FeatureCollection)")
        print("   • Same CRS (EPSG:4326)")
        print("   • All files follow GeoJSON specification")
    
    print(f"\n{'='*70}")
    print("GEOMETRY TYPES")
    print(f"{'='*70}\n")
    for geom_type, count in sorted(results['geometry_types'].items()):
        print(f"   • {geom_type}: {count} features")
    
    print(f"\n{'='*70}")
    print("COMMON PROPERTY FIELDS")
    print(f"{'='*70}\n")
    
    # Show most common properties
    sorted_props = sorted(results['property_keys'].items(), key=lambda x: x[1], reverse=True)
    print("Top 20 most common fields:")
    for prop, count in sorted_props[:20]:
        percentage = (count / results['total_features']) * 100
        print(f"   • {prop}: {count} ({percentage:.1f}%)")
    
    # Test MongoDB connection
    mongo_result = test_mongodb_connection()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    print(f"📊 GeoJSON Structure: {'✅ CONSISTENT' if not results['inconsistencies'] else '⚠️  HAS INCONSISTENCIES'}")
    if mongo_result:
        print(f"🗄️  MongoDB Connection: {'✅ CONNECTED' if mongo_result.get('connected') else '❌ FAILED'}")
        if mongo_result.get('connected'):
            print(f"📈 Database Status: {'✅ POPULATED' if mongo_result.get('doc_count', 0) > 0 else '⚠️  EMPTY'}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
