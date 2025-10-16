# 🗄️ MongoDB Database Setup

## 🚀 Quick Connection Guide (3 Steps)

### Step 1: Create MongoDB Atlas Account (FREE)

1. Go to: **https://www.mongodb.com/cloud/atlas/register**
2. Sign up with your email
3. Click **"Build a Database"**
4. Choose **"M0 FREE"** tier
5. Click **"Create"**

### Step 2: Set Up Access

#### A. Create Database User
1. Go to **"Database Access"** (left sidebar under Security)
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter:
   - Username: `hackathon_user` (or any name you want)
   - Password: Create a strong password (SAVE THIS!)
5. Set privileges to: **"Read and write to any database"**
6. Click **"Add User"**

#### B. Allow Network Access
1. Go to **"Network Access"** (left sidebar under Security)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (or add your IP)
4. Click **"Confirm"**

### Step 3: Get Connection String

1. Go to **"Database"** (left sidebar)
2. Click **"Connect"** button on your cluster
3. Choose **"Drivers"**
4. Select **"Python"** and version **"3.12 or later"**
5. Copy the connection string (looks like):
   ```
   mongodb+srv://hackathon_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **IMPORTANT**: Replace `<password>` with your actual password!

---

## 💻 Import Data to MongoDB

### 1. Create .env File

In the `databaze` directory, create a file named `.env`:

```bash
cd databaze
cp .env.example .env
nano .env  # or use any text editor
```

Paste your connection string:
```env
MONGODB_URI=mongodb+srv://hackathon_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=hackathon_hk
COLLECTION_NAME=places
```

**Replace `YOUR_PASSWORD` with your actual password!**

### 2. Run Setup Script

```bash
cd databaze
chmod +x setup.sh
./setup.sh
```

This will:
- Install Python virtual environment
- Install required packages (pymongo, python-dotenv)

### 3. Import All Data

```bash
source venv/bin/activate
python import_to_mongodb.py
```

This will:
- Connect to MongoDB Atlas
- Import all GeoJSON files from `data_hk/` and `data HK - rande geojson/`
- Create indexes for fast queries
- Show you statistics about imported data

### 4. Test Your Database

```bash
python query_mongodb.py
```

---

## 📊 What You Get

After import, you'll have:
- **One unified database** with all places/locations
- **Queryable by `dp_id`** (unique identifier)
- **Geospatial search** enabled (find places near coordinates)
- **Text search** enabled (search by name/description)
- **Cloud-hosted** on MongoDB Atlas (accessible from anywhere)

### Database Structure:
```json
{
  "dp_id": "HRAD1",
  "ds_id": "100001",
  "nazev": "Hrad Náchod",
  "popis": "Description...",
  "geometry": {
    "type": "Point",
    "coordinates": [16.1631, 50.4167]
  },
  "source_file": "data_hk_rande/Hrady.geojson",
  "nazev_vusc": "Královehradecký",
  "www": "http://...",
  "telefon": "+420...",
  ...
}
```

---

## 🔍 How to Query Your Database

### From Python:

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
print(place['nazev'])

# Search by name
results = collection.find({'nazev': {'$regex': 'Hrad', '$options': 'i'}})
for place in results:
    print(f"{place['nazev']} - {place['dp_id']}")

# Find nearby places (within 5km)
nearby = collection.find({
    'geometry': {
        '$near': {
            '$geometry': {
                'type': 'Point',
                'coordinates': [16.1631, 50.4167]  # [longitude, latitude]
            },
            '$maxDistance': 5000  # meters
        }
    }
}).limit(10)
```

### Using MongoDB Compass (GUI):

1. Download: https://www.mongodb.com/try/download/compass
2. Connect using your connection string
3. Browse and query visually

---

## 📁 Files in This Directory

- **`import_to_mongodb.py`** - Import script
- **`query_mongodb.py`** - Interactive query tool
- **`setup.sh`** - Setup script
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Template for your credentials
- **`MONGODB_SETUP.md`** - Detailed documentation
- **`QUICK_START.md`** - Quick reference guide

---

## ❓ Troubleshooting

**"Connection failed"**
- Check your `.env` file
- Make sure you replaced `<password>` with actual password
- Verify network access is allowed in MongoDB Atlas

**"Module not found"**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Run setup again: `./setup.sh`

**"Directory not found"**
- The script looks for data in parent directory (`../data_hk/` and `../data HK - rande geojson/`)
- Make sure you run the script from the `databaze` directory

---

## 🎯 Summary

1. **Create MongoDB Atlas account** (free)
2. **Create `.env` file** with your connection string
3. **Run `./setup.sh`**
4. **Run `python import_to_mongodb.py`**
5. **Done!** Your database is online and ready to use

**Need help?** Check `QUICK_START.md` or `MONGODB_SETUP.md` for more details.
