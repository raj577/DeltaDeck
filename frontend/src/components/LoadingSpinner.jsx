import React from 'react'

const LoadingSpinner = ({ message = 'Loading...', size = 'medium' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  }

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className={`loading-spinner ${sizeClasses[size]}`}></div>
      <p className="text-gray-600 dark:text-gray-400 text-sm">{message}</p>
    </div>
  )
}

export default LoadingSpinner