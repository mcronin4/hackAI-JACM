'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/lib/auth-store'

export default function AuthCallback() {
  const router = useRouter()
  const { checkAuthStatus } = useAuthStore()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Handle the OAuth callback
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Auth callback error:', error)
          router.push('/?error=auth_failed')
          return
        }

        if (data.session) {
          // Update auth store
          await checkAuthStatus()
          router.push('/')
        } else {
          router.push('/?error=no_session')
        }
      } catch (error) {
        console.error('Callback handling error:', error)
        router.push('/?error=callback_failed')
      }
    }

    handleAuthCallback()
  }, [router, checkAuthStatus])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Completing sign in...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we complete your X authentication.
          </p>
        </div>
      </div>
    </div>
  )
} 