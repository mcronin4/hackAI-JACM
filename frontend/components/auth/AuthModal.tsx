'use client'

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import LoginForm from './LoginForm'
import SignupForm from './SignupForm'
import { useAuthStore } from '@/lib/auth-store'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [isSyncingTwitter, setIsSyncingTwitter] = useState(false)
  const { checkAuthStatus } = useAuthStore()

  const handleLoginSuccess = async () => {
    await checkAuthStatus()
    onClose()
  }

  const handleSignupSuccess = async () => {
    console.log("Signup success")
    await checkAuthStatus()
    
    // Get fresh user data from store after auth check
    const currentUser = useAuthStore.getState().user
    console.log("Current User", currentUser)
    console.log("User ID", currentUser?.id)
    console.log("User X Handle", currentUser?.x_handle)
    
    // After signup, sync Twitter context
    if (currentUser?.id && currentUser?.x_handle) {
      setIsSyncingTwitter(true)
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/user/twitter-context', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: currentUser.id,
            twitter_handle: currentUser.x_handle
          })
        })

        const result = await response.json()
        
        if (!response.ok) {
          console.error('Twitter sync failed:', result)
          // Continue anyway - don't block the user
        }
      } catch (error) {
        console.error('Twitter sync error:', error)
        // Continue anyway - don't block the user
      } finally {
        setIsSyncingTwitter(false)
        onClose()
      }
    } else {
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-white bg-opacity-75 backdrop-blur-sm transition-opacity" onClick={onClose} />
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md">
          {/* Close button - top right */}
          <button
            onClick={onClose}
            className="absolute -top-8 -right-2 mt-13 mr-4 text-gray-700 hover:text-gray-900 transition-all duration-300 transform hover:scale-110 hover:rotate-90 p-2 rounded-full hover:bg-gray-100 z-10"
            aria-label="Close"
          >
            <X size={24} className="transition-transform duration-300" />
          </button>
          
          {/* Modal content */}
          <div className="relative bg-white rounded-lg shadow-xl">
            {isSyncingTwitter ? (
              <div className="p-8 text-center">
                <div className="flex flex-col items-center space-y-4">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Syncing your X profile
                    </h3>
                    <p className="text-sm text-gray-600">
                      We&apos;re setting up your content generation context...
                    </p>
                  </div>
                </div>
              </div>
            ) : isLogin ? (
              <LoginForm onSwitchToSignup={() => setIsLogin(false)} onSuccess={handleLoginSuccess} isModal />
            ) : (
              <SignupForm onSwitchToLogin={() => setIsLogin(true)} onSuccess={handleSignupSuccess} isModal />
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 