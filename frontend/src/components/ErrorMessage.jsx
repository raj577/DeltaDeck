import React from 'react'
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
            Error Loading Data
          </h3>
          <p className="text-sm text-red-700 dark:text-red-300 mt-1">
            {message}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 flex items-center space-x-2 text-sm text-red-800 dark:text-red-200 hover:text-red-900 dark:hover:text-red-100 font-medium"
            >
              <ArrowPathIcon className="h-4 w-4" />
              <span>Try Again</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorMessage