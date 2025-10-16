# Quick Start Guide - MongoDB Atlas Setup

## 📋 Summary

This project imports all GeoJSON files from your directories into a unified MongoDB Atlas database. Each place/location will have a unique identifier (`dp_id`) that you can use to query the database.

## 🚀 Quick Setup (5 minutes)

### 1. Create MongoDB Atlas Account (Free)

Visit: https://www.mongodb.com/cloud/atlas/register

- Sign up for free
- Create a new FREE cluster (M0)
- Set up a database user with username/password
- Allow network access from anywhere (or your IP)
- Get your connection string

### 2. Create .env File

Copy `.env.example` to `.env` and add your MongoDB Atlas connection string:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Your `.env` should look like:
```env
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=hackathon_hk
COLLECTION_NAME=places
```

### 3. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

### 4. Import Data to MongoDB Atlas

```bash
source venv/bin/activate
python import_to_mongodb.py
```

### 5. Test Your Database

```bash
python query_mongodb.py
```

## 📊 What Gets Imported

The script imports all GeoJSON files from:
- `data_hk/` directory (21 files)
- `data HK - rande geojson/` directory (21 files)

Each document contains:
- **dp_id**: Unique identifier (queryable)
- **ds_id**: Secondary identifier
- **nazev**: Name of the place
- **popis**: Description
- **geometry**: Location coordinates (GeoJSON format)
- **source_file**: Original file name
- All other properties from the GeoJSON files

## 🔍 Query Examples

### Query by dp_id:
```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['hackathon_hk']
collection = db['places']

# Find by unique ID
place = collection.find_one({'dp_id': 'HRAD1'})
print(place['nazev'])  # Name of the place
```

### Search by name:
```python
# Search for all castles (hrady)
results = collection.find({'nazev': {'$regex': 'hrad', '$options': 'i'}})
for place in results:
    print(f"{place['nazev']} - {place['dp_id']}")
```

### Geospatial query:
```python
# Find places near coordinates [longitude, latitude]
nearby = collection.find({
    'geometry': {
        '$near': {
            '$geometry': {
                'type': 'Point',
                'coordinates': [15.8, 50.2]  # [longitude, latitude]
            },
            '$maxDistance': 5000  # 5km radius
        }
    }
}).limit(10)
```

## 📝 Database Details

- **Database Name**: hackathon_hk
- **Collection Name**: places
- **Indexes Created**:
  - dp_id (for fast ID lookups)
  - ds_id (secondary ID)
  - geometry (2dsphere - for geospatial queries)
  - Text index on nazev and popis (for text search)

## 🌐 Access Your Database Online

Once imported, your data is in MongoDB Atlas cloud and accessible from anywhere with your connection string!

You can:
- Access via MongoDB Compass (GUI tool)
- Use the MongoDB Atlas web interface
- Query from any application using the connection string
- Build APIs on top of it

## 📚 Full Documentation

See `MONGODB_SETUP.md` for detailed step-by-step instructions.

## ❓ Troubleshooting

**Connection Error**: Check your `.env` file and ensure the connection string is correct

**Import Error**: Make sure virtual environment is activated (`source venv/bin/activate`)

**No data found**: Check that GeoJSON files exist in the directories

---

**Ready to start?** Follow steps 1-5 above! 🚀
