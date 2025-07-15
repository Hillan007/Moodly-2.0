# 🚀 SUPABASE SETUP GUIDE FOR MOODLY

## Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Sign up/Sign in to your account
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - Name: "Moodly App"
   - Database Password: (create a strong password)
   - Region: Choose closest to your users
6. Click "Create new project"

## Step 2: Get Your Supabase Credentials
After your project is created:
1. Go to Project Settings (gear icon)
2. Click "API" in the left sidebar
3. Copy these values:
   - **Project URL** (looks like: https://xxxxx.supabase.co)
   - **anon public key** (starts with: eyJhbGciOiJIUzI1NiIsInR5cCI...)

## Step 3: Create Storage Bucket
1. In your Supabase dashboard, go to "Storage" 
2. Click "Create a new bucket"
3. Bucket name: `profile-pictures`
4. Set it as **Public bucket** (check the box)
5. Click "Create bucket"

## Step 4: Set Up Storage Policies
1. Click on your `profile-pictures` bucket
2. Go to "Policies" tab
3. Click "Add policy" 
4. Choose "Custom policy"
5. Policy name: `Allow public uploads`
6. Allowed operation: `INSERT`, `SELECT`, `UPDATE`, `DELETE`
7. Target roles: `authenticated`, `anon`
8. Policy definition: `true` (allows all)
9. Click "Review" then "Save policy"

## Step 5: Add Environment Variables
Add these to your `.env` file:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

## Step 6: Test Your Setup
After adding the environment variables, restart your Flask app and try uploading a profile picture!

## 🎯 Benefits of Using Supabase:
- ✅ Works perfectly with Vercel serverless
- ✅ Permanent file storage (files don't get deleted)
- ✅ Fast global CDN for image delivery
- ✅ Automatic image optimization
- ✅ Free tier: 1GB storage + 2GB bandwidth/month
- ✅ Built-in authentication (for future features)

## 🔧 Troubleshooting:
- Make sure your bucket is set to **public**
- Double-check your environment variables
- Ensure storage policies allow public access
- Test the connection in your Flask logs

Ready to implement! 🚀
