#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection for IZA OS
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    # Test basic imports
    from dotenv import load_dotenv
    print("✅ dotenv import successful")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    print(f"✅ Environment variables loaded from {env_path}")
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    print(f"📊 Database URL: {database_url}")
    
    # Test direct psycopg2 connection
    try:
        import psycopg2
        print("✅ psycopg2 import successful")
        
        # Parse the connection string
        if database_url:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"🐘 PostgreSQL Version: {version[0]}")
            
            # Test basic operations
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"📅 Current Database: {db_name}")
            
            cursor.execute("SELECT current_user;")
            user = cursor.fetchone()[0]
            print(f"👤 Current User: {user}")
            
            # List tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"📋 Existing tables: {[table[0] for table in tables]}")
            else:
                print("📋 No tables found in public schema")
            
            cursor.close()
            conn.close()
            print("✅ Database connection test successful!")
            
        else:
            print("❌ DATABASE_URL not found in environment")
            
    except ImportError:
        print("❌ psycopg2 not installed")
        print("Installing psycopg2...")
        os.system("pip install psycopg2-binary")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
    # Test config loading
    try:
        from src.utils.config import load_config
        config = load_config()
        print("✅ IZA OS config loading successful")
        
        db_config = config.get('database', {})
        print(f"🔧 Database config: {db_config}")
        
    except ImportError as e:
        print(f"⚠️  IZA OS config import failed: {e}")
        print("This is expected if dependencies are not installed")
    except Exception as e:
        print(f"❌ Config loading error: {e}")

except ImportError as e:
    print(f"❌ Basic imports failed: {e}")
    print("Installing basic dependencies...")
    os.system("pip install python-dotenv psycopg2-binary")

except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "="*50)
print("Database connection test completed!")
