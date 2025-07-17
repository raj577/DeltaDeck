import React from 'react'
import { ArrowPathIcon, ChartBarIcon } from '@heroicons/react/24/outline'

const Header = ({ selectedSymbol, onSymbolChange, onRefresh, lastUpdated, loading }) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <ChartBarIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Option Spreads Analyzer
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Real-time NIFTY & BANKNIFTY spread recommendations
              </p>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Symbol Selector */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Symbol:
              </label>
              <select
                value={selectedSymbol}
                onChange={(e) => onSymbolChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="NIFTY">NIFTY</option>
                <option value="BANKNIFTY">BANKNIFTY</option>
              </select>
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md text-sm font-medium transition-colors"
            >
              <ArrowPathIcon className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            {/* Last Updated */}
            {lastUpdated && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <div>Last updated:</div>
                <div>{lastUpdated.toLocaleTimeString()}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header