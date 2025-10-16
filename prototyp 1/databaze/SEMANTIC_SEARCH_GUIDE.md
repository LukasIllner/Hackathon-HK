# Semantic Search Implementation Guide

## Current Status: NO RAG NEEDED for Basic Queries ✅

Your database **already supports** LLM queries through:
- ✅ Full-text search on names and descriptions
- ✅ Geospatial queries (near, within radius)
- ✅ Category/region filtering
- ✅ LLM function calling (GPT-4, Claude can construct MongoDB queries)

## When to Add RAG/Vector Search

Add semantic search if you need:
- **Semantic similarity:** "romantic spots" → cafes, theaters, parks
- **Conceptual queries:** "family activities" → ZOO, playgrounds, museums
- **Multi-language:** Search in English, find Czech results
- **Personalization:** User preferences and history

## Implementation Options

### Option 1: MongoDB Atlas Vector Search (Recommended)

**Pros:**
- Native MongoDB integration
- No additional database needed
- Simple to implement
- Free tier available

**Steps:**

1. **Generate Embeddings**
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# For each document:
text = f"{doc['nazev']} {doc.get('popis', '')}"
embedding = generate_embedding(text)
collection.update_one(
    {"_id": doc["_id"]},
    {"$set": {"embedding": embedding}}
)
```

2. **Create Vector Search Index** (In Atlas UI)
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

3. **Query with Vectors**
```python
def semantic_search(query_text):
    # Generate query embedding
    query_embedding = generate_embedding(query_text)
    
    # Vector search
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": 5
            }
        }
    ])
    return list(results)

# Now this works semantically!
results = semantic_search("romantic date spots")
```

**Cost:** 
- OpenAI embeddings: ~$0.13 per 1M tokens
- 1,018 documents ≈ $0.01 one-time
- Query embeddings: ~$0.0001 per query

### Option 2: External Vector Database

**Pinecone, Weaviate, Qdrant**

**Pros:**
- Specialized for vectors
- Advanced features
- Hybrid search

**Cons:**
- Additional service to manage
- More complex architecture

### Option 3: Local Embeddings (Free)

**Use sentence-transformers (no API cost)**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("your text here")
```

**Pros:**
- Free
- No API calls
- Privacy

**Cons:**
- Lower quality than OpenAI
- Requires local GPU for speed

## RAG Pipeline Architecture

```
User Query
    ↓
1. Generate query embedding
    ↓
2. Vector search (top 10 similar places)
    ↓
3. Re-rank by filters (location, category)
    ↓
4. Pass top 5 to LLM as context
    ↓
5. LLM generates natural language response
    ↓
User Response
```

## Recommendation

**For your hackathon project:**

### Phase 1: Use Current Setup (NOW)
- LLM function calling works great
- Text search covers 80% of use cases
- Geospatial queries are powerful
- **No additional cost or complexity**

### Phase 2: Add Vectors (If Needed)
- Use MongoDB Atlas Vector Search
- OpenAI embeddings (cheap, high quality)
- 1-2 hours implementation
- Enables semantic queries

## Example Use Cases

### Works NOW (Without RAG):
- ✅ "Find breweries" → text search
- ✅ "Museums near me" → geospatial + filter
- ✅ "Castles in Hradec Králové region" → structured query
- ✅ "Swimming pools" → text search "koupání"

### Needs RAG:
- ❌ "Romantic evening activities" → needs semantic understanding
- ❌ "Best spots for photographers" → needs concept linking
- ❌ "Rainy day activities" → needs inference (indoor places)

## Quick Start: Add Vector Search

If you want to add it now, run:

```bash
# Install dependencies
pip install openai sentence-transformers

# Generate embeddings
python generate_embeddings.py

# Create vector index in Atlas UI

# Update query functions
```

## Conclusion

**You DON'T need RAG right now.** Your database is fully queryable by LLMs using:
1. Function calling (GPT-4, Claude)
2. Text search
3. Geospatial queries
4. Structured filters

Add vector search later if you need true semantic understanding.
