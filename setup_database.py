"""
Database Setup Script for Fitness App

This script initializes the PostgreSQL database with the required tables.
Run this script before starting the Streamlit app for the first time.

Usage:
    python setup_database.py
"""

import os
import sys
from database import DatabaseManager

def main():
    """Initialize the database"""
    print("=" * 60)
    print("Fitness App - Database Setup")
    print("=" * 60)

    # Get database URL from environment variable
    db_url = os.getenv('DATABASE_URL')

    if not db_url:
        print("\n⚠️  WARNING: DATABASE_URL environment variable not set!")
        print("\nPlease set the DATABASE_URL environment variable with your PostgreSQL connection string.")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://username:password@localhost:5432/fitness_db'")
        print("\nOr create a .env file with:")
        print("  DATABASE_URL=postgresql://username:password@localhost:5432/fitness_db")
        print("\n" + "=" * 60)

        # Prompt user for database URL
        print("\nYou can enter the database URL now, or press Enter to exit:")
        user_input = input("DATABASE_URL: ").strip()

        if not user_input:
            print("Exiting without setting up database.")
            sys.exit(1)

        db_url = user_input

    print(f"\n📡 Connecting to database...")
    print(f"   Host: {db_url.split('@')[1] if '@' in db_url else 'unknown'}")

    try:
        # Create database manager
        db_manager = DatabaseManager(db_url)

        # Test connection
        print("\n🔍 Testing connection...")
        if not db_manager.test_connection():
            print("❌ Connection failed! Please check your DATABASE_URL and database server.")
            sys.exit(1)

        print("✅ Connection successful!")

        # Create tables
        print("\n📋 Creating database tables...")
        if db_manager.create_tables():
            print("✅ Tables created successfully!")
            print("\n📊 Created tables:")
            print("   - fitness_entries (stores workout and body metrics)")
            print("   - user_goals (stores user fitness goals)")
        else:
            print("❌ Failed to create tables!")
            sys.exit(1)

        # Summary
        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print("\nYou can now run your Streamlit app:")
        print("  streamlit run app.py")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials are correct")
        print("  3. Database exists (create it if needed)")
        print("  4. User has proper permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()
