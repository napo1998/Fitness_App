"""Simple connection test without Streamlit dependencies"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_url = os.getenv('DATABASE_URL')

print("=" * 60)
print("Testing Supabase Connection")
print("=" * 60)
print(f"\nConnection URL: {db_url[:50]}..." if db_url else "No DATABASE_URL found")

try:
    print("\nCreating engine...")
    engine = create_engine(db_url, echo=True)

    print("\nTesting connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"\n✓ Connection successful!")
        print(f"PostgreSQL version: {version[0][:50]}...")

    print("\n" + "=" * 60)
    print("✓ Database connection test PASSED!")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Connection failed!")
    print(f"Error: {e}")
    print("\n" + "=" * 60)
    print("✗ Database connection test FAILED!")
    print("=" * 60)
