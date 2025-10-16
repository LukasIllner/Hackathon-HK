#!/usr/bin/env python3
"""
Test and analyze MongoDB database - Check consistency and run test queries
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

def test_connection(client):
    """Test MongoDB connection"""
    try:
        client.admin.command('ping')
        print("✓ Connection successful")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def analyze_geometry_types(collection):
    """Analyze geometry types in the database"""
    print("\n" + "=" * 60)
    print("GEOMETRY TYPE ANALYSIS")
    print("=" * 60)
    
    pipeline = [
        {
            "$group": {
                "_id": "$geometry.type",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    print("\nGeometry types in database:")
    for result in results:
        geom_type = result['_id']
        count = result['count']
        print(f"  {geom_type}: {count} documents")
    
    # Check for polygons
    polygon_count = sum(r['count'] for r in results if 'Polygon' in str(r['_id']))
    if polygon_count > 0:
        print(f"\n⚠ WARNING: Found {polygon_count} polygon documents!")
    else:
        print("\n✓ No polygon geometries found")
    
    return results

def analyze_source_files(collection):
    """Analyze distribution by source file"""
    print("\n" + "=" * 60)
    print("SOURCE FILE DISTRIBUTION")
    print("=" * 60)
    
    pipeline = [
        {
            "$group": {
                "_id": "$source_file",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    print(f"\nTotal source files: {len(results)}")
    print("\nDocuments per source file:")
    for result in results:
        source = result['_id']
        count = result['count']
        print(f"  {count:4d} - {source}")
    
    return results

def check_required_fields(collection):
    """Check for required fields and data consistency"""
    print("\n" + "=" * 60)
    print("DATA CONSISTENCY CHECK")
    print("=" * 60)
    
    total_docs = collection.count_documents({})
    print(f"\nTotal documents: {total_docs}")
    
    # Check for required fields
    fields_to_check = ['geometry', 'nazev', 'dp_id', 'source_file', 'popis']
    
    print("\nField presence:")
    for field in fields_to_check:
        count = collection.count_documents({field: {"$exists": True, "$ne": None}})
        percentage = (count / total_docs * 100) if total_docs > 0 else 0
        status = "✓" if percentage > 95 else "⚠"
        print(f"  {status} {field}: {count}/{total_docs} ({percentage:.1f}%)")
    
    # Check for documents with missing coordinates
    missing_coords = collection.count_documents({
        "$or": [
            {"geometry": {"$exists": False}},
            {"geometry.coordinates": {"$exists": False}},
            {"geometry.coordinates": None}
        ]
    })
    
    if missing_coords > 0:
        print(f"\n⚠ WARNING: {missing_coords} documents missing coordinates")
    else:
        print("\n✓ All documents have coordinates")
    
    return total_docs

def test_queries(collection):
    """Run various test queries"""
    print("\n" + "=" * 60)
    print("TEST QUERIES")
    print("=" * 60)
    
    # Test 1: Find by dp_id
    print("\n1. Query by dp_id (HKFP1):")
    doc = collection.find_one({"dp_id": "HKFP1"})
    if doc:
        print(f"   ✓ Found: {doc.get('nazev', 'N/A')}")
        print(f"     Location: {doc.get('geometry', {}).get('coordinates', 'N/A')}")
    else:
        print("   ✗ Not found")
    
    # Test 2: Text search
    print("\n2. Text search for 'pivovar':")
    results = list(collection.find(
        {"$text": {"$search": "pivovar"}},
        {"nazev": 1, "popis": 1}
    ).limit(3))
    print(f"   Found {len(results)} results:")
    for doc in results:
        print(f"   - {doc.get('nazev', 'N/A')}")
    
    # Test 3: Geospatial query - find places near coordinates
    print("\n3. Geospatial query (near Hradec Králové):")
    # Hradec Králové approximate coordinates: [15.8333, 50.2097]
    results = list(collection.find({
        "geometry": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [15.8333, 50.2097]
                },
                "$maxDistance": 5000  # 5km
            }
        }
    }).limit(5))
    print(f"   Found {len(results)} places within 5km:")
    for doc in results:
        print(f"   - {doc.get('nazev', 'N/A')} ({doc.get('source_file', 'N/A')})")
    
    # Test 4: Count by region
    print("\n4. Count by region:")
    pipeline = [
        {"$group": {"_id": "$region", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    results = list(collection.aggregate(pipeline))
    for result in results:
        region = result['_id'] if result['_id'] else "(empty)"
        print(f"   {result['count']:4d} - {region}")
    
    # Test 5: Find documents with specific geometry type
    print("\n5. Count by geometry type:")
    pipeline = [
        {"$group": {"_id": "$geometry.type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(collection.aggregate(pipeline))
    for result in results:
        print(f"   {result['count']:4d} - {result['_id']}")

def check_indexes(collection):
    """Check database indexes"""
    print("\n" + "=" * 60)
    print("INDEX INFORMATION")
    print("=" * 60)
    
    indexes = collection.index_information()
    print(f"\nTotal indexes: {len(indexes)}")
    print("\nIndex details:")
    for index_name, index_info in indexes.items():
        print(f"  - {index_name}:")
        print(f"    Keys: {index_info.get('key', 'N/A')}")
        if 'unique' in index_info:
            print(f"    Unique: {index_info['unique']}")

def main():
    # Get MongoDB connection details
    mongodb_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
    collection_name = os.getenv('COLLECTION_NAME', 'places')
    
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not found!")
        return
    
    print("=" * 60)
    print("MongoDB Database Test & Analysis")
    print("=" * 60)
    print(f"\nDatabase: {database_name}")
    print(f"Collection: {collection_name}")
    print(f"Cloud: MongoDB Atlas")
    
    # Connect
    print("\nConnecting to MongoDB Atlas...")
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
        if not test_connection(client):
            return
    except Exception as e:
        print(f"Connection error: {e}")
        return
    
    db = client[database_name]
    collection = db[collection_name]
    
    # Run all tests
    check_required_fields(collection)
    analyze_geometry_types(collection)
    analyze_source_files(collection)
    check_indexes(collection)
    test_queries(collection)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Database: {database_name}")
    print(f"Collection: {collection_name}")
    print(f"Total Documents: {collection.count_documents({})}")
    print(f"Database Size: {db.command('dbStats')['dataSize'] / 1024 / 1024:.2f} MB")
    print("\n✓ Database analysis complete!")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    main()
