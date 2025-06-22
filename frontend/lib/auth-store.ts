import { create } from 'zustand'
import { supabase, UserProfile } from './supabase'

interface AuthState {
  user: UserProfile | null
  isLoggedIn: boolean
  isLoading: boolean
  
  // Actions
  signup: (email: string, xHandle: string, password: string) => Promise<{ success: boolean; error?: string }>
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => Promise<void>
  checkAuthStatus: () => Promise<void>
  resetAuthState: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoggedIn: false,
  isLoading: false,

  signup: async (email: string, xHandle: string, password: string) => {
    set({ isLoading: true })
    
    try {
      // Check if X handle already exists
      const { data: existingUser } = await supabase
        .from('user_info')
        .select('x_handle')
        .eq('x_handle', xHandle)
        .single()
      
      if (existingUser) {
        set({ isLoading: false })
        return { success: false, error: 'X handle already exists' }
      }

      // Check if email already exists
      const { data: existingEmail } = await supabase
        .from('user_info')
        .select('email')
        .eq('email', email)
        .single()
      
      if (existingEmail) {
        set({ isLoading: false })
        return { success: false, error: 'Email already exists' }
      }
      
      // Sign up with Supabase (this automatically hashes the password)
      const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password
      })
      
      if (error) {
        set({ isLoading: false })
        return { success: false, error: error.message }
      }
      
      if (data.user) {
        // Create user profile in user_info table
        const { error: profileError } = await supabase
          .from('user_info')
          .insert({
            user_id: data.user.id,
            username: xHandle, // Keep username field for compatibility
            x_handle: xHandle, // Store in X handle field
            email: email
          })
        
        if (profileError) {
          console.error('Profile creation error:', profileError)
          set({ isLoading: false })
          return { success: false, error: 'Failed to create user profile' }
        }
        
        // Get the created user profile
        const { data: userInfo } = await supabase
          .from('user_info')
          .select('*')
          .eq('user_id', data.user.id)
          .single()
        
        if (userInfo) {
          const userProfile: UserProfile = {
            id: data.user.id,
            email: userInfo.email,
            username: userInfo.username,
            full_name: userInfo.full_name,
            avatar_url: userInfo.avatar_url,
            x_oauth_token: null,
            x_oauth_secret: null,
            x_user_id: userInfo.x_user_id,
            x_screen_name: userInfo.x_screen_name,
            x_profile_image_url: userInfo.x_profile_image_url,
            x_handle: userInfo.x_handle,
            linkedin_handle: userInfo.linkedin_handle,
            created_at: userInfo.created_at,
            updated_at: userInfo.updated_at
          }
          
          set({ 
            isLoading: false, 
            isLoggedIn: true, 
            user: userProfile 
          })
          
          return { success: true }
        }
      }
      
      set({ isLoading: false })
      return { success: false, error: 'Failed to create account' }
      
    } catch (error) {
      console.error('Signup error:', error)
      set({ isLoading: false })
      return { success: false, error: 'An unexpected error occurred' }
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true })
    
    try {
      // Sign in with Supabase (this handles password verification)
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password
      })
      
      if (error) {
        set({ isLoading: false })
        return { success: false, error: error.message }
      }
      
      if (data.user) {
        // Get user profile
        const { data: userInfo } = await supabase
          .from('user_info')
          .select('*')
          .eq('user_id', data.user.id)
          .single()
        
        if (userInfo) {
          const userProfile: UserProfile = {
            id: data.user.id,
            email: userInfo.email,
            username: userInfo.username,
            full_name: userInfo.full_name,
            avatar_url: userInfo.avatar_url,
            x_oauth_token: null,
            x_oauth_secret: null,
            x_user_id: userInfo.x_user_id,
            x_screen_name: userInfo.x_screen_name,
            x_profile_image_url: userInfo.x_profile_image_url,
            x_handle: userInfo.x_handle,
            linkedin_handle: userInfo.linkedin_handle,
            created_at: userInfo.created_at,
            updated_at: userInfo.updated_at
          }
          
          set({ 
            isLoading: false, 
            isLoggedIn: true, 
            user: userProfile 
          })
          
          return { success: true }
        }
      }
      
      set({ isLoading: false })
      return { success: false, error: 'Login failed' }
      
    } catch (error) {
      console.error('Login error:', error)
      set({ isLoading: false })
      return { success: false, error: 'An unexpected error occurred' }
    }
  },

  logout: async () => {
    set({ isLoading: true })
    
    try {
      console.log('Attempting to logout...')
      
      // Sign out from Supabase
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        console.error('Logout error:', error)
      } else {
        console.log('Successfully logged out from server')
      }
      
      // Always clear user data locally
      set({ 
        user: null, 
        isLoggedIn: false,
        isLoading: false 
      })
      
      console.log('Local state cleared successfully')
      
    } catch (error) {
      console.error('Logout error:', error)
      // Even if there's an error, clear the local state
      set({ 
        user: null, 
        isLoggedIn: false,
        isLoading: false 
      })
    }
  },

  checkAuthStatus: async () => {
    set({ isLoading: true })
    
    try {
      console.log('Starting auth status check...')
      
      // Get current session
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error) {
        console.error('Session check error:', error)
        set({ isLoading: false, isLoggedIn: false, user: null })
        return
      }
      
      console.log('Session retrieved:', !!session)
      console.log('Session user exists:', !!session?.user)
      
      if (session?.user) {
        
        console.log('User ID:', session.user.id)
        console.log('User email:', session.user.email)
        
        // Get user info from our user_info table
        const { data: userInfo, error: userInfoError } = await supabase
          .from('user_info')
          .select('*')
          .eq('user_id', session.user.id)
          .single()
        
        console.log('User info query result:', { userInfo, userInfoError })
        
        if (userInfoError && userInfoError.code !== 'PGRST116') {
          console.error('User info fetch error:', userInfoError)
          set({ isLoading: false, isLoggedIn: false, user: null })
          return
        }
        
        if (userInfo) {
          // Create user profile from database data
          const userProfile: UserProfile = {
            id: session.user.id,
            email: userInfo.email || session.user.email,
            username: userInfo.username || null,
            full_name: userInfo.full_name || null,
            avatar_url: userInfo.avatar_url || null,
            x_oauth_token: null,
            x_oauth_secret: null,
            x_user_id: userInfo.x_user_id || null,
            x_screen_name: userInfo.x_screen_name || null,
            x_profile_image_url: userInfo.x_profile_image_url || null,
            x_handle: userInfo.x_handle || null,
            linkedin_handle: userInfo.linkedin_handle || null,
            created_at: userInfo.created_at || session.user.created_at,
            updated_at: userInfo.updated_at || null
          }
          
          set({ 
            isLoading: false, 
            isLoggedIn: true, 
            user: userProfile 
          })
        } else {
          set({ isLoading: false, isLoggedIn: false, user: null })
        }
      } else {
        set({ isLoading: false, isLoggedIn: false, user: null })
      }
    } catch (error) {
      console.error('Auth check error:', error)
      set({ isLoading: false, isLoggedIn: false, user: null })
    }
  },

  resetAuthState: () => {
    set({
      user: null,
      isLoggedIn: false,
      isLoading: false
    })
  },
})) 