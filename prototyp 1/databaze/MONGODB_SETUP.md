# MongoDB Atlas Setup Guide

## Step 1: Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up for a free account
3. Create a new cluster (choose the FREE tier - M0)

## Step 2: Configure Database Access

1. In Atlas, go to **Database Access** (in Security section)
2. Click **Add New Database User**
3. Create a username and password (save these!)
4. Set privileges to **Read and write to any database**

## Step 3: Configure Network Access

1. Go to **Network Access** (in Security section)
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (or add your specific IP)
4. Confirm

## Step 4: Get Connection String

1. Go to **Database** (in Deployment section)
2. Click **Connect** on your cluster
3. Choose **Connect your application**
4. Copy the connection string (should look like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<username>` and `<password>` with your actual credentials

## Step 5: Create .env File

Create a file named `.env` in this directory with the following content:

```env
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=hackathon_hk
COLLECTION_NAME=places
```

**Important:** Replace with your actual connection string!

## Step 6: Install Dependencies

### Option A: Using setup script (recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option B: Manual setup
```bash
# Install python3-venv if needed
sudo apt install python3-venv python3-full

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 7: Run Import Script

Make sure the virtual environment is activated:
```bash
source venv/bin/activate
python import_to_mongodb.py
```

This will:
- Connect to your MongoDB Atlas cluster
- Clear any existing data in the collection
- Import all GeoJSON files from both directories
- Create indexes for efficient querying
- Display sample documents and statistics

## Query Examples

Once imported, you can query the database. Here are some examples:

### Python Example:
```python
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['hackathon_hk']
collection = db['places']

# Query by dp_id
place = collection.find_one({'dp_id': 'HRAD1'})
print(place)

# Query by name
places = collection.find({'nazev': {'$regex': 'Hrad', '$options': 'i'}})
for place in places:
    print(place['nazev'])

# Geospatial query (find places within 10km of a point)
places = collection.find({
    'geometry': {
        '$near': {
            '$geometry': {
                'type': 'Point',
                'coordinates': [15.8, 50.2]
            },
            '$maxDistance': 10000  # 10km in meters
        }
    }
})
```

## Database Structure

Each document in the database contains:
- `dp_id`: Unique identifier from the source data
- `ds_id`: Additional identifier
- `nazev`: Name of the place
- `popis`: Description
- `geometry`: GeoJSON geometry (Point, Polygon, etc.)
- `source_file`: Which file the data came from
- All other properties from the original GeoJSON files

## Indexes Created

- `dp_id`: For fast lookups by ID
- `ds_id`: Additional ID index
- `geometry`: Geospatial index (2dsphere) for location-based queries
- Text index on `nazev` and `popis` for text search
