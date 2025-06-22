import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for user profile - matches the expanded user_info table structure
export interface UserProfile {
  id: string // maps to user_id
  email: string | null
  username: string | null
  full_name: string | null
  avatar_url: string | null
  x_oauth_token: string | null
  x_oauth_secret: string | null
  x_user_id: string | null
  x_screen_name: string | null
  x_profile_image_url: string | null
  x_handle: string | null
  linkedin_handle: string | null
  created_at: string
  updated_at: string | null
} 