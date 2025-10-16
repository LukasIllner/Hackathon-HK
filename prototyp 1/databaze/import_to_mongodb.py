#!/usr/bin/env python3
"""
Import all GeoJSON files into MongoDB Atlas
"""
import json
import os
from pathlib import Path
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_geojson_file(filepath):
    """Read and parse a GeoJSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_features(geojson_data, source_file):
    """Extract features from GeoJSON and add metadata"""
    features = []
    
    if geojson_data.get('type') == 'FeatureCollection':
        for feature in geojson_data.get('features', []):
            # Combine geometry and properties into a single document
            document = {
                'geometry': feature.get('geometry'),
                'source_file': source_file,
                'type': feature.get('type'),
            }
            
            # Add all properties to the document
            properties = feature.get('properties', {})
            document.update(properties)
            
            features.append(document)
    
    return features

def import_geojson_directory(directory_path, collection, source_prefix):
    """Import all GeoJSON files from a directory"""
    # Adjust path to go up one directory from databaze folder
    base_path = Path(__file__).parent.parent
    directory = base_path / directory_path
    
    if not directory.exists():
        print(f"Directory {directory_path} does not exist, skipping...")
        return 0
    
    total_imported = 0
    geojson_files = list(directory.glob('*.geojson'))
    
    print(f"\nProcessing {len(geojson_files)} files from {directory_path}...")
    
    for filepath in geojson_files:
        try:
            print(f"  Reading {filepath.name}...")
            geojson_data = read_geojson_file(filepath)
            
            source_file = f"{source_prefix}/{filepath.name}"
            features = extract_features(geojson_data, source_file)
            
            if features:
                # Insert documents
                result = collection.insert_many(features)
                imported_count = len(result.inserted_ids)
                total_imported += imported_count
                print(f"    ✓ Imported {imported_count} documents")
            else:
                print(f"    ⚠ No features found in {filepath.name}")
                
        except Exception as e:
            print(f"    ✗ Error processing {filepath.name}: {e}")
    
    return total_imported

def main():
    # Get MongoDB connection details from environment
    mongodb_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
    collection_name = os.getenv('COLLECTION_NAME', 'places')
    
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not found in environment variables!")
        print("Please create a .env file with your MongoDB Atlas connection string.")
        print("See .env.example for reference.")
        return
    
    print("=" * 60)
    print("MongoDB Import Script - Hackathon HK")
    print("=" * 60)
    
    # Connect to MongoDB
    print(f"\nConnecting to MongoDB Atlas...")
    print("(This may take a moment if the cluster is just starting up...)")
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
        # Test connection
        client.admin.command('ping')
        print("✓ Connected successfully!")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Get database and collection
    db = client[database_name]
    collection = db[collection_name]
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print(f"\nClearing existing data from {database_name}.{collection_name}...")
    result = collection.delete_many({})
    print(f"✓ Deleted {result.deleted_count} existing documents")
    
    # Import from both directories
    total = 0
    
    # Import from data_hk directory
    total += import_geojson_directory('data_hk', collection, 'data_hk')
    
    # Import from data HK - rande geojson directory
    total += import_geojson_directory('data HK - rande geojson', collection, 'data_hk_rande')
    
    print("\n" + "=" * 60)
    print(f"TOTAL IMPORTED: {total} documents")
    print("=" * 60)
    
    # Create indexes for better query performance
    print("\nCreating indexes...")
    
    # Index on dp_id (unique identifier)
    if total > 0:
        # Check if dp_id exists in documents
        sample_doc = collection.find_one({})
        if sample_doc and 'dp_id' in sample_doc:
            collection.create_index([("dp_id", ASCENDING)], unique=False)
            print("✓ Created index on 'dp_id'")
        
        # Index on ds_id if it exists
        if sample_doc and 'ds_id' in sample_doc:
            collection.create_index([("ds_id", ASCENDING)])
            print("✓ Created index on 'ds_id'")
        
        # Geospatial index for location queries
        collection.create_index([("geometry", "2dsphere")])
        print("✓ Created geospatial index on 'geometry'")
        
        # Text index for searching by name
        if sample_doc and 'nazev' in sample_doc:
            collection.create_index([("nazev", "text"), ("popis", "text")])
            print("✓ Created text index on 'nazev' and 'popis'")
    
    # Display sample query
    print("\n" + "=" * 60)
    print("Sample documents in database:")
    print("=" * 60)
    
    for doc in collection.find().limit(3):
        print(f"\n{doc.get('nazev', 'No name')}")
        print(f"  dp_id: {doc.get('dp_id', 'N/A')}")
        print(f"  Source: {doc.get('source_file', 'N/A')}")
        print(f"  Location: {doc.get('geometry', {}).get('coordinates', 'N/A')}")
    
    # Print connection info
    print("\n" + "=" * 60)
    print("Database Information:")
    print("=" * 60)
    print(f"Database: {database_name}")
    print(f"Collection: {collection_name}")
    print(f"Total Documents: {collection.count_documents({})}")
    
    print("\n✓ Import completed successfully!")
    print("\nYou can now query the database using dp_id, ds_id, or other fields.")
    
    client.close()

if __name__ == "__main__":
    main()
