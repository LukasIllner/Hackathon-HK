#!/usr/bin/env python3
"""
Simple script to query the MongoDB database
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    mongodb_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
    collection_name = os.getenv('COLLECTION_NAME', 'places')
    
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not found in .env file!")
        return
    
    # Connect to MongoDB
    print("Connecting to MongoDB Atlas...")
    client = MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]
    
    # Show database stats
    total_docs = collection.count_documents({})
    print(f"\nTotal documents in database: {total_docs}")
    
    # Query by dp_id
    print("\n" + "="*60)
    print("Example 1: Query by dp_id")
    print("="*60)
    
    dp_id = input("Enter dp_id to search (or press Enter to skip): ").strip()
    if dp_id:
        result = collection.find_one({'dp_id': dp_id})
        if result:
            print(f"\nFound:")
            print(f"  Name: {result.get('nazev', 'N/A')}")
            print(f"  Description: {result.get('popis', 'N/A')}")
            print(f"  Location: {result.get('geometry', {}).get('coordinates', 'N/A')}")
            print(f"  Source: {result.get('source_file', 'N/A')}")
        else:
            print(f"No document found with dp_id: {dp_id}")
    
    # Text search
    print("\n" + "="*60)
    print("Example 2: Search by name")
    print("="*60)
    
    search_term = input("Enter search term (or press Enter to skip): ").strip()
    if search_term:
        results = collection.find({'nazev': {'$regex': search_term, '$options': 'i'}}).limit(10)
        count = 0
        for doc in results:
            count += 1
            print(f"\n{count}. {doc.get('nazev', 'N/A')}")
            print(f"   ID: {doc.get('dp_id', 'N/A')}")
            print(f"   Type: {doc.get('source_file', 'N/A')}")
        
        if count == 0:
            print(f"No results found for: {search_term}")
    
    # Show sample documents
    print("\n" + "="*60)
    print("Sample Documents (first 5):")
    print("="*60)
    
    for i, doc in enumerate(collection.find().limit(5), 1):
        print(f"\n{i}. {doc.get('nazev', 'N/A')}")
        print(f"   dp_id: {doc.get('dp_id', 'N/A')}")
        print(f"   Source: {doc.get('source_file', 'N/A')}")
    
    # Get unique dp_id count
    unique_dp_ids = len(collection.distinct('dp_id'))
    print(f"\n\nTotal unique dp_ids: {unique_dp_ids}")
    
    client.close()
    print("\n✓ Query completed!")

if __name__ == "__main__":
    main()
