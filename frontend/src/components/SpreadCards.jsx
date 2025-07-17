import React, { useState, useEffect } from 'react'
import { 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  ChartBarIcon,
  CurrencyRupeeIcon,
  ScaleIcon
} from '@heroicons/react/24/outline'

const SpreadCards = ({ recommendations, symbol, loading, onRefresh }) => {
  const [animatedRecommendations, setAnimatedRecommendations] = useState([])
  const [isAnimating, setIsAnimating] = useState(false)

  // Handle recommendations update with animation
  useEffect(() => {
    if (recommendations && recommendations.length > 0) {
      setIsAnimating(true)
      
      // Fade out existing cards
      setTimeout(() => {
        setAnimatedRecommendations(recommendations)
        setIsAnimating(false)
      }, 300)
    } else {
      setAnimatedRecommendations([])
    }
  }, [recommendations])

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatNumber = (num, decimals = 2) => {
    return Number(num).toFixed(decimals)
  }

  const getSpreadTypeIcon = (type) => {
    return type.includes('Bull') ? (
      <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
    ) : (
      <ArrowTrendingDownIcon className="h-6 w-6 text-red-600" />
    )
  }

  const getSpreadTypeColor = (type) => {
    return type.includes('Bull') 
      ? 'from-green-50 to-green-100 border-green-200' 
      : 'from-red-50 to-red-100 border-red-200'
  }

  const getSpreadTypeTextColor = (type) => {
    return type.includes('Bull') ? 'text-green-800' : 'text-red-800'
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {symbol} Spread Recommendations
          </h2>
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        {/* Loading skeleton cards */}
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-xl shadow-md p-6 animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="h-6 bg-gray-200 rounded w-24"></div>
              <div className="h-6 bg-gray-200 rounded w-16"></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!animatedRecommendations || animatedRecommendations.length === 0) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Spread Recommendations
        </h3>
        <p className="text-gray-500 mb-6">
          No profitable spreads found for {symbol} with current market conditions.
        </p>
        <button
          onClick={onRefresh}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Refresh Recommendations
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            {symbol} Spread Recommendations
          </h2>
          <div className="flex items-center space-x-4 mt-2">
            <p className="text-sm text-gray-600 font-medium">
              {animatedRecommendations.length} opportunities found
            </p>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-xs text-blue-700 font-semibold bg-blue-100 px-2 py-1 rounded-full">
                Delta range: 0.15-0.26
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl text-sm font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <span className="text-lg">🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* Spread Cards */}
      <div className={`grid gap-6 transition-opacity duration-300 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
        {animatedRecommendations.map((spread, index) => {
          // Debug: Log the spread data structure
          console.log('Spread data:', spread)
          return (
          <div
            key={`${spread.type}-${spread.buy_strike}-${spread.sell_strike}`}
            className={`bg-gradient-to-br ${getSpreadTypeColor(spread.type)} rounded-2xl shadow-xl border-2 p-8 transform transition-all duration-500 hover:scale-105 hover:shadow-2xl backdrop-blur-sm`}
            style={{
              animationDelay: `${index * 150}ms`,
              animation: isAnimating ? 'none' : 'fadeInUp 0.8s ease-out forwards'
            }}
          >
            {/* Card Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                {getSpreadTypeIcon(spread.type)}
                <div>
                  <h3 className={`text-lg font-bold ${getSpreadTypeTextColor(spread.type)}`}>
                    {spread.type}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Expiry: {spread.expiry}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center space-x-1 text-sm text-gray-600">
                  <ScaleIcon className="h-4 w-4" />
                  <span>Delta: {formatNumber(spread.delta_difference, 4)}</span>
                </div>
                <div className={`text-lg font-bold ${getSpreadTypeTextColor(spread.type)}`}>
                  Risk:Reward 1:{formatNumber(spread.risk_reward_ratio)}
                </div>
              </div>
            </div>

            {/* Strike Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Buy Leg */}
              <div className="bg-white/70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-semibold text-green-800">Buy Leg</span>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 text-sm font-medium">Strike:</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-xl text-gray-900">{spread.buy_strike || 'N/A'}</span>
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                        {spread.type.includes('Bull') ? 'CE' : 'PE'}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 text-sm font-medium">Delta:</span>
                    <span className="font-semibold text-lg text-gray-800 bg-gray-100 px-3 py-1 rounded-lg">
                      {spread.buy_delta !== undefined && spread.buy_delta !== null ? formatNumber(spread.buy_delta, 4) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Sell Leg */}
              <div className="bg-white/70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="font-semibold text-red-800">Sell Leg</span>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 text-sm font-medium">Strike:</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-xl text-gray-900">{spread.sell_strike || 'N/A'}</span>
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full">
                        {spread.type.includes('Bull') ? 'CE' : 'PE'}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 text-sm font-medium">Delta:</span>
                    <span className="font-semibold text-lg text-gray-800 bg-gray-100 px-3 py-1 rounded-lg">
                      {spread.sell_delta !== undefined && spread.sell_delta !== null ? formatNumber(spread.sell_delta, 4) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>


          </div>
        )})}
      </div>
    </div>
  )
}

// Add CSS animation keyframes
const style = document.createElement('style')
style.textContent = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`
document.head.appendChild(style)

export default SpreadCards