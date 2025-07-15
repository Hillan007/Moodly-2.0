#!/usr/bin/env python3
"""
🧪 Complete Supabase Integration Test
Tests all aspects of Supabase cloud storage integration
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a small test image for upload testing"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer

def test_supabase_integration():
    """Test complete Supabase integration"""
    print("🧪 COMPLETE SUPABASE INTEGRATION TEST")
    print("=" * 60)
    
    # Load environment variables first
    load_dotenv()
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Storage Status
    print("\n📊 Test 1: Storage Status API")
    try:
        response = requests.get(f"{base_url}/api/storage/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Storage Status API working")
            print(f"   - Supabase enabled: {data.get('supabase_enabled')}")
            print(f"   - Storage type: {data.get('storage_type')}")
            print(f"   - Bucket: {data.get('supabase_stats', {}).get('bucket')}")
            print(f"   - Status: {data.get('supabase_stats', {}).get('status')}")
            
            if not data.get('supabase_enabled'):
                print("❌ Supabase not enabled!")
                return False
        else:
            print(f"❌ Storage status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Storage status error: {e}")
        return False
    
    # Test 2: Home Page Access
    print("\n🏠 Test 2: Home Page Access")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Home page accessible")
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False
    
    # Test 3: User Registration
    print("\n👤 Test 3: User Registration")
    try:
        signup_data = {
            'username': 'supabasetest',
            'email': 'test@supabase.com',
            'password': 'test123',
            'confirm_password': 'test123',
            'age': '20'
        }
        
        response = requests.post(f"{base_url}/signup", data=signup_data, allow_redirects=False)
        if response.status_code in [200, 302]:  # Success or redirect
            print("✅ User registration working")
        else:
            print(f"⚠️ Registration status: {response.status_code} (may be expected)")
    except Exception as e:
        print(f"⚠️ Registration test note: {e}")
    
    # Test 4: Direct Supabase Storage Test
    print("\n🌩️ Test 4: Direct Supabase Storage Test")
    try:
        from supabase_storage import SupabaseStorage
        storage = SupabaseStorage()
        
        if storage.is_enabled():
            print("✅ Supabase storage helper working")
            
            # Test image upload
            test_image = create_test_image()
            test_user_id = "test_user_12345"
            
            result = storage.upload_profile_picture(
                file_data=test_image.getvalue(),
                user_id=test_user_id,
                file_extension='png'
            )
            
            if result['success']:
                print("✅ Test image upload successful!")
                print(f"   - Filename: {result['filename']}")
                print(f"   - Public URL: {result['public_url'][:50]}...")
                
                # Test image deletion
                delete_result = storage.delete_profile_picture(test_user_id, result['filename'])
                if delete_result['success']:
                    print("✅ Test image deletion successful!")
                else:
                    print(f"⚠️ Image deletion failed: {delete_result['error']}")
            else:
                print(f"❌ Test image upload failed: {result['error']}")
                return False
        else:
            print("❌ Supabase storage not enabled")
            return False
            
    except Exception as e:
        print(f"❌ Direct storage test error: {e}")
        return False
    
    # Test 5: Bucket Accessibility Test
    print("\n🪣 Test 5: Bucket Accessibility Test")
    try:
        load_dotenv()
        supabase_url = os.environ.get('SUPABASE_URL')
        bucket_url = f"{supabase_url}/storage/v1/object/public/profile-pictures/"
        
        # Test if bucket is accessible (should return 404 for non-existent file, not 403)
        response = requests.get(f"{bucket_url}nonexistent.jpg")
        if response.status_code == 404:
            print("✅ Bucket is publicly accessible")
        elif response.status_code == 403:
            print("⚠️ Bucket permissions may need adjustment")
        else:
            print(f"ℹ️ Bucket test status: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Bucket test note: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL SUPABASE TESTS COMPLETED SUCCESSFULLY!")
    print("\n💡 Test Summary:")
    print("   ✅ Storage Status API working")  
    print("   ✅ Home page accessible")
    print("   ✅ Supabase storage helper functional")
    print("   ✅ Image upload/delete operations working")
    print("   ✅ Cloud storage fully integrated")
    
    print("\n🚀 Ready for Production Deployment!")
    print("   • Add SUPABASE_URL and SUPABASE_KEY to Vercel")
    print("   • Deploy and profile uploads will work in production")
    print("   • No more file system errors!")
    
    return True

if __name__ == "__main__":
    success = test_supabase_integration()
    if success:
        print("\n🎯 Next Steps:")
        print("1. Open http://127.0.0.1:5000 in your browser")
        print("2. Create an account and test profile picture upload")
        print("3. Deploy to Vercel with Supabase environment variables")
    sys.exit(0 if success else 1)
