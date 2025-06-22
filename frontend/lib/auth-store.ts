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
}

export const useAuthStore = create<AuthState>((set: any, get: any) => ({
  user: null,
  isLoggedIn: false,
  isLoading: false,

  loginWithX: async () => {
    set({ isLoading: true })
    
    try {
      // For now, we'll simulate the OAuth flow
      // In the next step, we'll implement the actual X OAuth
      console.log('Starting X OAuth flow...')
      
      // Simulate OAuth redirect
      // This will be replaced with actual OAuth implementation
      setTimeout(() => {
        set({ 
          isLoading: false,
          isLoggedIn: true,
          user: {
            id: 'demo-user-id',
            email: 'demo@example.com',
            username: 'demo_user',
            full_name: 'Demo User',
            avatar_url: null,
            x_oauth_token: 'demo-token',
            x_oauth_secret: 'demo-secret',
            x_user_id: '123456789',
            x_screen_name: 'demo_user',
            x_profile_image_url: 'https://pbs.twimg.com/profile_images/1234567890/demo_400x400.jpg',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        })
      }, 2000)
      
    } catch (error) {
      console.error('Login error:', error)
      set({ isLoading: false })
    }
  },

  logout: async () => {
    set({ isLoading: true })
    
    try {
      // Clear user data
      set({ 
        user: null, 
        isLoggedIn: false,
        isLoading: false 
      })
    } catch (error) {
      console.error('Logout error:', error)
      set({ isLoading: false })
    }
  },

  checkAuthStatus: async () => {
    set({ isLoading: true })
    
    try {
      // Check if user is logged in
      // This will be implemented with actual Supabase auth check
      set({ isLoading: false })
    } catch (error) {
      console.error('Auth check error:', error)
      set({ isLoading: false })
    }
  },
})) 