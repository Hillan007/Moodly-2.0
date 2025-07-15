#!/usr/bin/env python3
"""
🧪 Supabase Connection Test Script
Tests the Supabase integration for Moodly app
"""

import os
import sys
from dotenv import load_dotenv

def test_supabase_connection():
    """Test Supabase connection step by step"""
    print("🧪 SUPABASE CONNECTION TEST")
    print("=" * 50)
    
    # Step 1: Load environment
    print("📁 Loading environment variables...")
    load_dotenv()
    
    # Step 2: Check environment variables
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    print(f"🔗 SUPABASE_URL: {'✅ Found' if url else '❌ Missing'}")
    print(f"🔑 SUPABASE_KEY: {'✅ Found' if key else '❌ Missing'}")
    
    if not url or not key:
        print("\n❌ Missing Supabase credentials!")
        print("💡 Check your .env file")
        return False
    
    # Step 3: Test Supabase import
    print("\n📦 Testing Supabase import...")
    try:
        from supabase import create_client
        print("✅ Supabase package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import supabase: {e}")
        return False
    
    # Step 4: Create client
    print("\n🌩️ Creating Supabase client...")
    try:
        client = create_client(url, key)
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Step 5: Test storage helper
    print("\n📂 Testing storage helper...")
    try:
        from supabase_storage import SupabaseStorage
        storage = SupabaseStorage()
        print(f"✅ Storage helper initialized: {storage.is_enabled()}")
        
        if storage.is_enabled():
            print("🌩️ SUPABASE CLOUD STORAGE READY!")
        else:
            print("⚠️ Storage helper created but Supabase not available")
            
    except Exception as e:
        print(f"❌ Storage helper failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Supabase is ready to use!")
    return True

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
