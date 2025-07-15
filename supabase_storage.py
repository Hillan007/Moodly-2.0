"""
Supabase Storage Helper for Moodly App
Handles profile picture uploads to Supabase Storage
"""
import os
import uuid
from io import BytesIO
from PIL import Image
from supabase import create_client, Client
import requests

class SupabaseStorage:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️ Supabase credentials not found in environment variables")
            self.client = None
            self.enabled = False
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                self.bucket_name = 'profile-pictures'
                self.enabled = True
                print("✅ Supabase storage initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase: {e}")
                self.client = None
                self.enabled = False
    
    def is_enabled(self):
        """Check if Supabase storage is available"""
        return self.enabled and self.client is not None
    
    def upload_profile_picture(self, file_data, user_id, file_extension='jpg'):
        """
        Upload profile picture to Supabase Storage
        
        Args:
            file_data: File data (bytes or file-like object)
            user_id: User ID for organizing files
            file_extension: File extension (jpg, png, etc.)
            
        Returns:
            dict: Success status and public URL or error message
        """
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'Supabase storage not available'
            }
        
        try:
            # Generate unique filename
            filename = f"{user_id}/profile_{uuid.uuid4().hex}.{file_extension}"
            
            # If file_data is a file-like object, read it
            if hasattr(file_data, 'read'):
                file_bytes = file_data.read()
            else:
                file_bytes = file_data
            
            # Resize image before upload
            resized_image_bytes = self._resize_image(file_bytes)
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(self.bucket_name).upload(
                file=resized_image_bytes,
                path=filename,
                file_options={
                    "content-type": f"image/{file_extension}",
                    "upsert": True  # Overwrite if exists
                }
            )
            
            if result.status_code == 200 or result.status_code == 201:
                # Get public URL
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)
                
                print(f"✅ Successfully uploaded profile picture: {filename}")
                return {
                    'success': True,
                    'public_url': public_url,
                    'filename': filename
                }
            else:
                print(f"❌ Upload failed: {result}")
                return {
                    'success': False,
                    'error': f'Upload failed: {result.status_code}'
                }
                
        except Exception as e:
            print(f"❌ Error uploading to Supabase: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_profile_picture(self, filename):
        """
        Delete profile picture from Supabase Storage
        
        Args:
            filename: The filename/path to delete
            
        Returns:
            bool: Success status
        """
        if not self.is_enabled():
            return False
        
        try:
            result = self.client.storage.from_(self.bucket_name).remove([filename])
            if result:
                print(f"✅ Successfully deleted file: {filename}")
                return True
            else:
                print(f"⚠️ File may not exist: {filename}")
                return False
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
    
    def _resize_image(self, image_bytes, max_size=(400, 400), quality=85):
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image_bytes: Raw image bytes
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            
        Returns:
            bytes: Resized image bytes
        """
        try:
            # Open image from bytes
            image = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            print(f"📸 Image resized to {image.size}")
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Error resizing image: {e}")
            # Return original bytes if resize fails
            return image_bytes
    
    def get_storage_stats(self):
        """Get storage usage statistics"""
        if not self.is_enabled():
            return None
            
        try:
            # This would require additional Supabase API calls
            # For now, return basic info
            return {
                'enabled': True,
                'bucket': self.bucket_name,
                'status': 'connected'
            }
        except Exception as e:
            print(f"❌ Error getting storage stats: {e}")
            return None

# Global instance
supabase_storage = SupabaseStorage()
