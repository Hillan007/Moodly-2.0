"""
Verify that nuclear deployment eliminated the line 51 error
"""
import requests
import time

def verify_deployment():
    print("🔍 VERIFYING NUCLEAR DEPLOYMENT")
    print("=" * 40)
    
    # Your Vercel URL (update this)
    vercel_url = "https://moodly-2-0-b654r4y7h-hillan007s-projects.vercel.app"
    
    print(f"Testing URL: {vercel_url}")
    
    # Test multiple endpoints
    endpoints = [
        "/",
        "/health",
        "/api/storage/status"
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing: {endpoint}")
        try:
            response = requests.get(f"{vercel_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS - No line 51 error!")
            elif response.status_code == 500:
                print("❌ Still getting 500 error")
                print("Response:", response.text[:200])
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(2)  # Don't spam the server
    
    print("\n🎯 NUCLEAR DEPLOYMENT VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_deployment()