"""
Quick Supabase Setup Script for Fitness App

This interactive script helps you set up Supabase PostgreSQL for your fitness app.
"""

import os
import sys

def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print("  🏋️ FITNESS APP - SUPABASE SETUP 🏋️")
    print("="*70)

def print_instructions():
    """Print setup instructions"""
    print("\n📋 BEFORE YOU START:")
    print("   1. Create a Supabase account at https://supabase.com")
    print("   2. Create a new project")
    print("   3. Get your connection string from:")
    print("      Dashboard > Settings > Database > Connection string (URI)")
    print("\n" + "-"*70)

def get_connection_string():
    """Get database connection string from user"""
    print("\n🔗 ENTER YOUR SUPABASE CONNECTION STRING:")
    print("   (It looks like: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres)")
    print("\n   Paste it here and press Enter:")

    connection_string = input("   > ").strip()

    if not connection_string:
        print("\n❌ No connection string provided. Exiting.")
        sys.exit(1)

    if not connection_string.startswith("postgresql://"):
        print("\n❌ Invalid connection string. It should start with 'postgresql://'")
        sys.exit(1)

    return connection_string

def save_to_env_file(connection_string):
    """Save connection string to .env file"""
    env_file = ".env"

    try:
        with open(env_file, 'w') as f:
            f.write(f"# Supabase PostgreSQL Connection\n")
            f.write(f"DATABASE_URL={connection_string}\n")

        print(f"\n✅ Saved to {env_file}")
        return True
    except Exception as e:
        print(f"\n⚠️  Could not save to {env_file}: {e}")
        return False

def test_and_setup_database(connection_string):
    """Test connection and create tables"""
    print("\n🔧 Setting up database...")

    try:
        # Set environment variable temporarily
        os.environ['DATABASE_URL'] = connection_string

        # Import after setting env var
        from database import DatabaseManager

        print("   📡 Testing connection...")
        db_manager = DatabaseManager(connection_string)

        if not db_manager.test_connection():
            print("   ❌ Connection failed!")
            return False

        print("   ✅ Connection successful!")

        print("   📋 Creating tables...")
        if db_manager.create_tables():
            print("   ✅ Tables created successfully!")
            print("\n   📊 Created tables:")
            print("      - fitness_entries (stores workout data)")
            print("      - user_goals (stores fitness goals)")
            return True
        else:
            print("   ❌ Failed to create tables!")
            return False

    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return False

def print_next_steps():
    """Print what to do next"""
    print("\n" + "="*70)
    print("  ✅ SETUP COMPLETE!")
    print("="*70)
    print("\n📱 NEXT STEPS:")
    print("   1. Install dependencies:")
    print("      pip install -r requirements.txt")
    print("\n   2. Run your app:")
    print("      streamlit run app.py")
    print("\n   3. View your data in Supabase:")
    print("      Dashboard > Table Editor")
    print("\n" + "="*70)

def main():
    """Main setup flow"""
    print_header()
    print_instructions()

    # Get connection string
    connection_string = get_connection_string()

    # Save to .env file
    save_to_env_file(connection_string)

    # Setup database
    if test_and_setup_database(connection_string):
        print_next_steps()
    else:
        print("\n" + "="*70)
        print("  ❌ SETUP FAILED")
        print("="*70)
        print("\n🔍 TROUBLESHOOTING:")
        print("   • Check your connection string is correct")
        print("   • Verify your password doesn't have special characters")
        print("     (If it does, URL-encode them: @ → %40, # → %23)")
        print("   • Make sure your Supabase project is running")
        print("   • Try adding '?sslmode=require' at the end of the URL")
        print("\n   For more help, see SUPABASE_SETUP.md")
        print("="*70)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
