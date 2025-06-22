# Supabase Authentication Setup Guide

## Overview
Your application now uses Supabase's built-in authentication system with username/password login. Supabase automatically handles password hashing and security for you.

## Setup Steps

### 1. Create Environment File
Create a `.env.local` file in your `frontend` directory:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Get Supabase Credentials
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings** → **API**
4. Copy the **Project URL** and **anon public** key
5. Replace the placeholder values in your `.env.local` file

### 3. Database Schema
Your current schema is already set up correctly. The key tables are:

- `auth.users` - Supabase's built-in user table (handles password hashing)
- `public.user_info` - Your custom user profile table
- Other content tables for your application

### 4. Row Level Security (RLS)
Make sure RLS is enabled on your tables. Run this in your Supabase SQL editor:

```sql
-- Enable RLS on all tables
ALTER TABLE public.user_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.longform_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.existing_context_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.linkedin_tokens ENABLE ROW LEVEL SECURITY;

-- User info policies
CREATE POLICY "Users can view their own user info" ON public.user_info
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own user info" ON public.user_info
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own user info" ON public.user_info
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own user info" ON public.user_info
    FOR DELETE USING (auth.uid() = user_id);

-- Content policies
CREATE POLICY "Users can view their own content" ON public.longform_content
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own content" ON public.longform_content
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own content" ON public.longform_content
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own content" ON public.longform_content
    FOR DELETE USING (auth.uid() = user_id);

-- Generated posts policies
CREATE POLICY "Users can view their own generated posts" ON public.generated_posts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own generated posts" ON public.generated_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own generated posts" ON public.generated_posts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own generated posts" ON public.generated_posts
    FOR DELETE USING (auth.uid() = user_id);

-- Existing context posts policies
CREATE POLICY "Users can view their own existing context posts" ON public.existing_context_posts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own existing context posts" ON public.existing_context_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own existing context posts" ON public.existing_context_posts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own existing context posts" ON public.existing_context_posts
    FOR DELETE USING (auth.uid() = user_id);
```

### 5. Authentication Settings
In your Supabase dashboard:

1. Go to **Authentication** → **Settings**
2. Under **Site URL**, add your development URL (e.g., `http://localhost:3000`)
3. Under **Redirect URLs**, add your callback URL (e.g., `http://localhost:3000/auth/callback`)

### 6. Test the System
1. Start your frontend: `npm run dev`
2. Click the "Sign Up / Login" button in the top right
3. Try creating a new account
4. Try logging in with the created account

## How It Works

### Password Security
- **Supabase automatically hashes passwords** using industry-standard bcrypt
- Passwords are never stored in plain text
- Password verification is handled securely by Supabase

### User Flow
1. **Signup**: User enters username/password → Supabase creates auth user → Profile created in `user_info` table
2. **Login**: User enters username → System looks up email → Supabase verifies password → User logged in
3. **Session**: Supabase manages JWT tokens automatically

### Database Structure
- `auth.users` - Supabase's secure user table (handles authentication)
- `public.user_info` - Your custom profile table (stores additional user data)
- Foreign key relationship ensures data integrity

## Security Features
- ✅ Passwords automatically hashed by Supabase
- ✅ JWT tokens for session management
- ✅ Row Level Security (RLS) policies
- ✅ SQL injection protection
- ✅ CSRF protection
- ✅ Rate limiting (handled by Supabase)

## Troubleshooting

### Common Issues
1. **"Invalid API key"** - Check your environment variables
2. **"Table doesn't exist"** - Run the SQL schema in Supabase
3. **"RLS policy violation"** - Check your RLS policies
4. **"Username already exists"** - Username validation is working correctly

### Debug Mode
Check the browser console for detailed error messages. The auth store includes comprehensive logging.

## Next Steps
Once authentication is working, you can:
1. Add email verification
2. Implement password reset
3. Add social login providers
4. Customize the user profile fields
5. Add user roles and permissions 