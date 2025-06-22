'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import LoginForm from './LoginForm'
import SignupForm from './SignupForm'
import { useAuthStore } from '@/lib/auth-store'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true)
  const { checkAuthStatus } = useAuthStore()

  const handleSuccess = async () => {
    await checkAuthStatus()
    onClose()
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
            {isLogin ? (
              <LoginForm onSwitchToSignup={() => setIsLogin(false)} onSuccess={handleSuccess} isModal />
            ) : (
              <SignupForm onSwitchToLogin={() => setIsLogin(true)} onSuccess={handleSuccess} isModal />
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 