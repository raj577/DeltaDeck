import React from 'react'
import { TrendingUpIcon, TrendingDownIcon } from '@heroicons/react/24/outline'

const PriceDisplay = ({ prices, selectedSymbol }) => {
  const niftyPrice = prices?.NIFTY?.ltp || 0
  const bankniftyPrice = prices?.BANKNIFTY?.ltp || 0
  
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  const PriceCard = ({ symbol, price, isSelected }) => (
    <div className={`p-6 rounded-lg border-2 transition-all ${
      isSelected 
        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
        : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
    }`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className={`text-lg font-semibold ${
            isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'
          }`}>
            {symbol}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {symbol === 'NIFTY' ? 'NIFTY 50 Index' : 'BANK NIFTY Index'}
          </p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${
            isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'
          }`}>
            {formatPrice(price)}
          </div>
          <div className="flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUpIcon className="h-4 w-4 mr-1" />
            <span>Live</span>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <PriceCard 
        symbol="NIFTY" 
        price={niftyPrice} 
        isSelected={selectedSymbol === 'NIFTY'} 
      />
      <PriceCard 
        symbol="BANKNIFTY" 
        price={bankniftyPrice} 
        isSelected={selectedSymbol === 'BANKNIFTY'} 
      />
    </div>
  )
}

export default PriceDisplay