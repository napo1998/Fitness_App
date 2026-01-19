# Supabase PostgreSQL Setup Guide

This guide will walk you through setting up your Fitness App with Supabase as the PostgreSQL database backend.

## Why Supabase?

- ✅ **Free Tier Available** - 500MB database, perfect for this app
- ✅ **Easy Setup** - No complex configuration needed
- ✅ **Cloud-Hosted** - Access your data from anywhere
- ✅ **Automatic Backups** - Built-in backup system
- ✅ **Fast & Reliable** - Great performance worldwide

## Step-by-Step Setup

### Step 1: Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" or "Sign Up"
3. Sign up with GitHub, Google, or email

### Step 2: Create a New Project

1. After logging in, click **"New Project"**
2. Fill in the project details:
   - **Name**: `fitness-tracker` (or any name you prefer)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your location
   - **Pricing Plan**: Select "Free" tier

3. Click **"Create new project"**
4. Wait 2-3 minutes for Supabase to set up your database

### Step 3: Get Your Database Connection String

1. In your Supabase project dashboard, click on the **"Settings"** icon (gear icon) in the left sidebar
2. Click on **"Database"** in the settings menu
3. Scroll down to **"Connection string"** section
4. Select the **"URI"** tab (not Session mode or Transaction mode)
5. You'll see a connection string like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. Click the **copy** icon to copy it
7. **IMPORTANT**: Replace `[YOUR-PASSWORD]` with the actual database password you created in Step 2

### Step 4: Configure Your App

#### Option A: Using Environment Variable (Recommended)

**Windows (Command Prompt):**
```cmd
set DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
```

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres"
```

**Mac/Linux:**
```bash
export DATABASE_URL='postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres'
```

#### Option B: Using .env File (Recommended for Development)

1. Create a `.env` file in your Fitness_App folder:
   ```bash
   # Windows Command Prompt
   type nul > .env

   # Mac/Linux
   touch .env
   ```

2. Edit the `.env` file and add:
   ```
   DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
   ```

3. Install python-dotenv to load .env automatically:
   ```bash
   pip install python-dotenv
   ```

### Step 5: Initialize the Database

Run the setup script to create the required tables:

```bash
python setup_database.py
```

You should see:
```
===========================================================
Fitness App - Database Setup
===========================================================

📡 Connecting to database...
   Host: db.xxxxx.supabase.co:5432/postgres

🔍 Testing connection...
✅ Connection successful!

📋 Creating database tables...
✅ Tables created successfully!

📊 Created tables:
   - fitness_entries (stores workout and body metrics)
   - user_goals (stores user fitness goals)

===========================================================
✅ Database setup complete!
===========================================================
```

### Step 6: Run Your App

```bash
streamlit run app.py
```

The app will now use Supabase for data storage!

## Verify Setup in Supabase Dashboard

1. Go back to your Supabase project dashboard
2. Click on **"Table Editor"** in the left sidebar
3. You should see two new tables:
   - `fitness_entries`
   - `user_goals`

## Connection String Breakdown

```
postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
    │          │        │              │                    │      │
    │          │        │              │                    │      └─ Database name
    │          │        │              │                    └─ Port
    │          │        │              └─ Supabase host
    │          │        └─ Your password
    │          └─ Username (default: postgres)
    └─ Protocol
```

## Deployment Options

### Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. In deployment settings, add **Secrets**:
   ```toml
   DATABASE_URL = "postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres"
   ```
5. Deploy!

### Deploy to Heroku

1. Create a Heroku app
2. Set the config var:
   ```bash
   heroku config:set DATABASE_URL='postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres'
   ```
3. Deploy your app

### Deploy to Render

1. Create a new Web Service on Render
2. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: `postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres`
3. Deploy

## Troubleshooting

### Error: "connection refused" or "timeout"

**Solution**: Check if SSL is required. Update your connection string:
```
postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

### Error: "password authentication failed"

**Solutions**:
1. Make sure you replaced `[YOUR-PASSWORD]` with your actual password
2. Check if there are special characters in your password - they might need URL encoding:
   - `@` → `%40`
   - `#` → `%23`
   - `&` → `%26`
   - `=` → `%3D`

Example with special characters:
```
# If password is: Pass@123#
# Use: Pass%40123%23
postgresql://postgres:Pass%40123%23@db.xxxxx.supabase.co:5432/postgres
```

### Error: "SSL connection required"

Add `?sslmode=require` to your connection string:
```
postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

### Can't find .env file

Make sure:
1. The `.env` file is in the same directory as `app.py`
2. You've installed python-dotenv: `pip install python-dotenv`
3. The database.py module loads it (already configured)

### Database tables not created

Run the setup script again:
```bash
python setup_database.py
```

Or check tables in Supabase:
1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Verify `fitness_entries` and `user_goals` tables exist

## Supabase Features You Can Use

### 1. View Your Data

In Supabase Dashboard:
- Go to **Table Editor**
- Click on `fitness_entries` to see all workout data
- Click on `user_goals` to see user goals

### 2. Run SQL Queries

In Supabase Dashboard:
- Go to **SQL Editor**
- Run custom queries:
  ```sql
  -- See all users
  SELECT DISTINCT user FROM fitness_entries;

  -- See latest entries
  SELECT * FROM fitness_entries ORDER BY date DESC LIMIT 10;

  -- Count entries per user
  SELECT user, COUNT(*) as entry_count
  FROM fitness_entries
  GROUP BY user;
  ```

### 3. Database Backups

Supabase automatically backs up your database daily (on free tier).

### 4. API Access (Optional)

Supabase provides REST and GraphQL APIs if you want to build a mobile app later!

## Security Best Practices

### 1. Never Commit Your .env File

Add to `.gitignore`:
```
.env
*.env
```

### 2. Use Environment Variables in Production

Never hardcode the DATABASE_URL in your code.

### 3. Reset Password if Exposed

If you accidentally expose your password:
1. Go to Supabase Dashboard > Settings > Database
2. Click "Reset Database Password"
3. Update your DATABASE_URL with the new password

### 4. Enable Row Level Security (Optional)

For production apps, you can enable RLS in Supabase:
1. Go to Authentication settings
2. Enable Row Level Security
3. Create policies for your tables

## Monitoring & Limits

### Free Tier Limits:
- **Database size**: 500 MB
- **Bandwidth**: 2 GB per month
- **API requests**: 500,000 per month

To check usage:
1. Go to Supabase Dashboard
2. Click "Settings" > "Usage"

## Migration from File Storage

Your app will automatically handle data migration:

1. **First run with Supabase**: App loads existing CSV/JSON files
2. **When you save new data**: It saves to both Supabase and local files
3. **All existing data preserved**: Nothing is lost

To force migration of all existing data:
- Simply add a new entry in the app
- Or manually insert data via Supabase SQL Editor

## Support & Resources

- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Supabase Community**: [https://github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
- **Connection Issues**: [Supabase Database Guide](https://supabase.com/docs/guides/database)

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                  SUPABASE QUICK REFERENCE                │
├─────────────────────────────────────────────────────────┤
│ 1. Get connection string:                                │
│    Dashboard > Settings > Database > Connection string   │
│                                                           │
│ 2. Set environment variable:                             │
│    export DATABASE_URL='postgresql://...'                │
│                                                           │
│ 3. Initialize database:                                  │
│    python setup_database.py                              │
│                                                           │
│ 4. Run app:                                              │
│    streamlit run app.py                                  │
│                                                           │
│ 5. View data:                                            │
│    Supabase Dashboard > Table Editor                     │
└─────────────────────────────────────────────────────────┘
```

---

**Ready to go!** Your Fitness App is now powered by Supabase PostgreSQL. All your data is securely stored in the cloud and accessible from anywhere. 🚀
