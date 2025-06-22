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
      // Use Supabase's built-in X OAuth
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'twitter',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
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
        }
        
        // If user_info doesn't exist, create it with X OAuth data
        if (!userInfo && session.user) {
          console.log('No existing user info found, creating new record...')
          
          // Debug: Log the user metadata to see what we're getting
          console.log('Session user:', session.user)
          console.log('User metadata:', session.user.user_metadata)
          
          // First, let's test if we can access the table at all
          console.log('Testing database access...')
          const { error: testError } = await supabase
            .from('user_info')
            .select('count')
            .limit(1)
          
          console.log('Database access test:', { testError })
          
          // Prepare the data we're trying to insert
          const userDataToInsert = {
            user_id: session.user.id,
            email: session.user.email,
            username: session.user.user_metadata?.preferred_username,
            full_name: session.user.user_metadata?.full_name,
            avatar_url: session.user.user_metadata?.avatar_url,
            x_oauth_token: session.user.user_metadata?.access_token,
            x_oauth_secret: session.user.user_metadata?.access_token_secret,
            x_user_id: session.user.user_metadata?.provider_id,
            x_handle: session.user.user_metadata?.preferred_username,
            x_screen_name: session.user.user_metadata?.preferred_username,
            x_profile_image_url: session.user.user_metadata?.avatar_url
          }
          
          console.log('Attempting to insert user data:', userDataToInsert)
          
          try {
            const { data: newUserInfo, error: createError } = await supabase
              .from('user_info')
              .insert(userDataToInsert)
              .select()
              .single()
            
            if (createError) {
              console.error('User info creation error:', createError)
              console.error('Error details:', {
                message: createError.message,
                details: createError.details,
                hint: createError.hint,
                code: createError.code
              })
              throw createError
            } else {
              console.log('Successfully created user info:', newUserInfo)
              const userProfile: UserProfile = {
                id: session.user.id,
                email: newUserInfo.email || session.user.email,
                username: newUserInfo.username || null,
                full_name: newUserInfo.full_name || null,
                avatar_url: newUserInfo.avatar_url || null,
                x_oauth_token: newUserInfo.x_oauth_token || null,
                x_oauth_secret: newUserInfo.x_oauth_secret || null,
                x_user_id: newUserInfo.x_user_id || null,
                x_screen_name: newUserInfo.x_screen_name || null,
                x_profile_image_url: newUserInfo.x_profile_image_url || null,
                x_handle: newUserInfo.x_handle || null,
                linkedin_handle: newUserInfo.linkedin_handle || null,
                created_at: newUserInfo.created_at,
                updated_at: newUserInfo.updated_at || null
              }
              
              set({ 
                isLoading: false, 
                isLoggedIn: true, 
                user: userProfile 
              })
              return
            }
          } catch (error) {
            console.error('User info creation error:', error)
            set({ isLoading: false, isLoggedIn: false, user: null })
          }
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