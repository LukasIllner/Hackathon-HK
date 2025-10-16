#!/usr/bin/env python3
"""
Example: How an LLM can query the MongoDB database
Shows both current capabilities and semantic search approach
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import json

load_dotenv()

class DatabaseQueryAgent:
    """Agent that can query the database based on natural language"""
    
    def __init__(self):
        mongodb_uri = os.getenv('MONGODB_URI')
        database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
        collection_name = os.getenv('COLLECTION_NAME', 'places')
        
        self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
    
    def query_by_intent(self, user_query: str):
        """
        Simulate how an LLM would interpret a user query and construct MongoDB query
        In production, the LLM would use function calling to build these queries
        """
        
        print(f"\n{'='*60}")
        print(f"User Query: {user_query}")
        print(f"{'='*60}")
        
        # Example queries an LLM could construct:
        
        if "pivovar" in user_query.lower() or "brewery" in user_query.lower():
            return self._find_breweries()
        
        elif "museum" in user_query.lower() or "muzeum" in user_query.lower():
            return self._find_museums()
        
        elif "near" in user_query.lower() and "hradec" in user_query.lower():
            return self._find_near_hradec_kralove()
        
        elif "castle" in user_query.lower() or "hrad" in user_query.lower():
            return self._find_castles()
        
        elif "sport" in user_query.lower():
            return self._find_sports()
        
        else:
            # Fallback: text search
            return self._text_search(user_query)
    
    def _find_breweries(self):
        """Find all breweries"""
        query = {"$text": {"$search": "pivovar"}}
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps(query, indent=2))
        print(f"\nResults: {len(results)} breweries")
        for doc in results:
            print(f"  - {doc.get('nazev')} ({doc.get('region', 'N/A')})")
        
        return results
    
    def _find_museums(self):
        """Find museums"""
        # Can search by source file or text
        query = {"source_file": {"$regex": "Muzea"}}
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps({"source_file": {"$regex": "Muzea"}}, indent=2))
        print(f"\nResults: {len(results)} museums")
        for doc in results:
            print(f"  - {doc.get('nazev')} ({doc.get('region', 'N/A')})")
        
        return results
    
    def _find_near_hradec_kralove(self):
        """Find places near Hradec Králové"""
        query = {
            "geometry": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [15.8333, 50.2097]  # Hradec Králové
                    },
                    "$maxDistance": 10000  # 10km
                }
            }
        }
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps(query, indent=2))
        print(f"\nResults: {len(results)} places within 10km")
        for doc in results:
            coords = doc.get('geometry', {}).get('coordinates', [])
            print(f"  - {doc.get('nazev')} at {coords}")
        
        return results
    
    def _find_castles(self):
        """Find castles and fortresses"""
        query = {"source_file": {"$regex": "Hrady|Zámky"}}
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps({"source_file": {"$regex": "Hrady|Zámky"}}, indent=2))
        print(f"\nResults: {len(results)} castles")
        for doc in results:
            print(f"  - {doc.get('nazev')} ({doc.get('region', 'N/A')})")
        
        return results
    
    def _find_sports(self):
        """Find sports activities"""
        query = {"source_file": {"$regex": "sport|koupání"}}
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps({"source_file": {"$regex": "sport|koupání"}}, indent=2))
        print(f"\nResults: {len(results)} sports activities")
        for doc in results:
            print(f"  - {doc.get('nazev')} ({doc.get('region', 'N/A')})")
        
        return results
    
    def _text_search(self, query_text):
        """Generic text search"""
        query = {"$text": {"$search": query_text}}
        results = list(self.collection.find(query).limit(5))
        
        print("\nMongoDB Query:")
        print(json.dumps(query, indent=2))
        print(f"\nResults: {len(results)} matches")
        for doc in results:
            print(f"  - {doc.get('nazev')} ({doc.get('region', 'N/A')})")
        
        return results
    
    def close(self):
        self.client.close()


def demonstrate_llm_queries():
    """Demonstrate how LLM would query the database"""
    
    print("="*60)
    print("LLM Database Query Examples")
    print("="*60)
    print("\nThis demonstrates how an LLM can query MongoDB")
    print("using function calling (no RAG needed for basic queries)")
    
    agent = DatabaseQueryAgent()
    
    # Example queries an LLM would process
    example_queries = [
        "Find me some breweries in the region",
        "Show me museums",
        "What's near Hradec Králové?",
        "I want to visit a castle",
        "Find sports activities"
    ]
    
    for query in example_queries:
        agent.query_by_intent(query)
        print()
    
    print("\n" + "="*60)
    print("SEMANTIC SEARCH (Would Need RAG)")
    print("="*60)
    print("""
For these types of queries, you'd need vector embeddings + RAG:

❌ "romantic date spots" 
   → Needs to understand cafes, restaurants, parks are romantic
   
❌ "family-friendly activities"
   → Needs to understand ZOO, playgrounds, museums are family-friendly
   
❌ "historical landmarks"
   → Needs semantic understanding of what's historical
   
❌ "outdoor adventures"
   → Needs to connect hiking, sports, nature activities

To enable this, you would:
1. Generate embeddings for each place's description
2. Store vectors in MongoDB Atlas Vector Search
3. Use $vectorSearch for semantic queries
4. Implement RAG pipeline for context-aware responses
""")
    
    print("\n" + "="*60)
    print("CURRENT CAPABILITIES (Without RAG)")
    print("="*60)
    print("""
✅ Keyword search (text search on names/descriptions)
✅ Category filtering (by source file, region)
✅ Geospatial queries (near location, within radius)
✅ Structured queries (by dp_id, dates, etc.)
✅ LLM function calling (construct queries from intent)

These work RIGHT NOW without any additional setup!
""")
    
    agent.close()


if __name__ == "__main__":
    demonstrate_llm_queries()
