'use client'

import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '@/lib/auth-store'
import { XLogo } from '@/lib/x-logo'
import { LogOut } from 'lucide-react'

interface ProfileDropdownProps {
  user: any
  isLoading: boolean
  onLogout: () => void
}

export function ProfileDropdown({ user, isLoading, onLogout }: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const toggleDropdown = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Profile Picture Button */}
      <button
        onClick={toggleDropdown}
        disabled={isLoading}
        className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200 hover:border-gray-300 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        {user?.x_profile_image_url ? (
          <img
            src={user.x_profile_image_url}
            alt={user.x_screen_name || 'Profile'}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <XLogo className="w-5 h-5 text-gray-600" />
          </div>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
          {/* User Info Section */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full overflow-hidden">
                {user?.x_profile_image_url ? (
                  <img
                    src={user.x_profile_image_url}
                    alt={user.x_screen_name || 'Profile'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                    <XLogo className="w-5 h-5 text-gray-600" />
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || user?.username || 'User'}
                </p>
                <p className="text-sm text-gray-500 truncate">
                  @{user?.x_screen_name || 'username'}
                </p>
              </div>
            </div>
          </div>

          {/* Logout Section */}
          <div className="pt-1">
            <button
              onClick={() => {
                setIsOpen(false)
                onLogout()
              }}
              disabled={isLoading}
              className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3 transition-colors duration-150 disabled:opacity-50"
            >
              <LogOut className="w-4 h-4" />
              <span>{isLoading ? 'Logging out...' : 'Logout'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 