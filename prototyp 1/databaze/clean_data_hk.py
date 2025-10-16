#!/usr/bin/env python3
"""
Remove all data_hk documents from MongoDB
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

def main():
    mongodb_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
    collection_name = os.getenv('COLLECTION_NAME', 'places')
    
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not found in .env file!")
        return
    
    print("=" * 60)
    print("Cleaning data_hk documents from MongoDB")
    print("=" * 60)
    
    # Connect to MongoDB
    print("\nConnecting to MongoDB Atlas...")
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
    
    try:
        client.admin.command('ping')
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    db = client[database_name]
    collection = db[collection_name]
    
    # Count documents before
    total_before = collection.count_documents({})
    data_hk_count = collection.count_documents({'source_file': {'$regex': '^data_hk/'}})
    
    print(f"\n📊 Current database state:")
    print(f"   Total documents: {total_before}")
    print(f"   Documents from data_hk/: {data_hk_count}")
    
    # Delete data_hk documents
    if data_hk_count > 0:
        result = collection.delete_many({'source_file': {'$regex': '^data_hk/'}})
        print(f"\n🗑️  Deleted {result.deleted_count} documents from data_hk/")
    else:
        print("\n✅ No data_hk documents found to delete")
    
    # Count after
    total_after = collection.count_documents({})
    print(f"\n📊 After cleanup:")
    print(f"   Total documents: {total_after}")
    print(f"   Remaining documents: {total_after}")
    
    # Show remaining sources
    if total_after > 0:
        print(f"\n📁 Remaining data sources:")
        pipeline = [
            {"$group": {"_id": "$source_file", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        for result in collection.aggregate(pipeline):
            if result['_id']:
                print(f"   • {result['_id']}: {result['count']} documents")
    
    client.close()
    print("\n✅ Cleanup completed!")

if __name__ == "__main__":
    main()
