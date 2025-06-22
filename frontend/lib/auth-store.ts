import { create } from 'zustand'
import { supabase, UserProfile } from './supabase'

interface AuthState {
  user: UserProfile | null
  isLoggedIn: boolean
  isLoading: boolean
  
  // Actions
  loginWithX: () => Promise<void>
  logout: () => Promise<void>
  checkAuthStatus: () => Promise<void>
  resetAuthState: () => void
}

export const useAuthStore = create<AuthState>((set: any, get: any) => ({
  user: null,
  isLoggedIn: false,
  isLoading: false,

  loginWithX: async () => {
    set({ isLoading: true })
    
    try {
      // Use Supabase's built-in X OAuth
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'twitter',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      if (error) {
        console.error('X OAuth error:', error)
        set({ isLoading: false })
        throw error
      }
      
      // The redirect will happen automatically
      // We don't need to set user data here as it will be handled in the callback
      
    } catch (error) {
      console.error('Login error:', error)
      set({ isLoading: false })
    }
  },

  logout: async () => {
    set({ isLoading: true })
    
    try {
      console.log('Attempting to logout...')
      
      // Try to sign out from Supabase
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        console.error('Logout error:', error)
        // Even if server logout fails, we should clear local state
        console.log('Server logout failed, but clearing local state...')
      } else {
        console.log('Successfully logged out from server')
      }
      
      // Always clear user data locally, regardless of server response
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
        
        // Get user info from our expanded user_info table
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
          const { data: testData, error: testError } = await supabase
            .from('user_info')
            .select('count')
            .limit(1)
          
          console.log('Database access test:', { testData, testError })
          
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
        
        // Create user profile from database data
        const userProfile: UserProfile = {
          id: session.user.id,
          email: userInfo?.email || session.user.email,
          username: userInfo?.username || null,
          full_name: userInfo?.full_name || null,
          avatar_url: userInfo?.avatar_url || null,
          x_oauth_token: userInfo?.x_oauth_token || null,
          x_oauth_secret: userInfo?.x_oauth_secret || null,
          x_user_id: userInfo?.x_user_id || null,
          x_screen_name: userInfo?.x_screen_name || null,
          x_profile_image_url: userInfo?.x_profile_image_url || null,
          x_handle: userInfo?.x_handle || null,
          linkedin_handle: userInfo?.linkedin_handle || null,
          created_at: userInfo?.created_at || session.user.created_at,
          updated_at: userInfo?.updated_at || null
        }
        
        set({ 
          isLoading: false, 
          isLoggedIn: true, 
          user: userProfile 
        })
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