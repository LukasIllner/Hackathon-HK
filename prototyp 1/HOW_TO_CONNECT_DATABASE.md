# 🔌 How to Connect MongoDB Database

All database files are now in the **`databaze/`** directory.

## 📝 What You Need to Do (3 Simple Steps)

### 1️⃣ Create FREE MongoDB Atlas Account

Visit: **https://www.mongodb.com/cloud/atlas/register**

- Sign up (free)
- Create a FREE cluster (M0)
- Create a database user (username + password)
- Allow network access from anywhere
- Get your connection string

### 2️⃣ Create .env File

```bash
cd databaze
cp .env.example .env
nano .env  # Edit this file
```

Add your MongoDB connection string:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=hackathon_hk
COLLECTION_NAME=places
```

**Replace `username` and `password` with your actual credentials!**

### 3️⃣ Run the Import

```bash
cd databaze
./setup.sh                    # Install dependencies
source venv/bin/activate      # Activate environment
python import_to_mongodb.py   # Import all data to MongoDB Atlas
```

---

## ✅ That's It!

Your database will be:
- ☁️ **Online** in MongoDB Atlas cloud
- 🌍 **Accessible from anywhere**
- 🔍 **Queryable by `dp_id`** and other fields
- 📍 **Geospatial search enabled**

---

## 📖 Detailed Instructions

See **`databaze/README.md`** for:
- Step-by-step MongoDB Atlas setup
- How to query the database
- Code examples
- Troubleshooting

---

## 🗂️ What Gets Imported

All GeoJSON files from:
- `data_hk/` (21 files)
- `data HK - rande geojson/` (21 files)

Into one unified database where you can query by `dp_id`.
