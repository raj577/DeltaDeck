import React, { useState } from 'react'
import { 
  ChevronUpIcon, 
  ChevronDownIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from './LoadingSpinner'

const RecommendationsTable = ({ recommendations, symbol, loading, onRefresh }) => {
  const [sortField, setSortField] = useState('risk_reward_ratio')
  const [sortDirection, setSortDirection] = useState('desc')
  const [expandedRow, setExpandedRow] = useState(null)

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const sortedRecommendations = [...recommendations].sort((a, b) => {
    const aVal = a[sortField]
    const bVal = b[sortField]
    const multiplier = sortDirection === 'asc' ? 1 : -1
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return (aVal - bVal) * multiplier
    }
    return String(aVal).localeCompare(String(bVal)) * multiplier
  })

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
      <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />
    ) : (
      <ArrowTrendingDownIcon className="h-4 w-4 text-red-600" />
    )
  }

  const SortHeader = ({ field, children }) => (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortDirection === 'asc' ? 
            <ChevronUpIcon className="h-4 w-4" /> : 
            <ChevronDownIcon className="h-4 w-4" />
        )}
      </div>
    </th>
  )

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          {symbol} Spread Recommendations
        </h2>
        <LoadingSpinner message="Loading spread recommendations..." />
      </div>
    )
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          {symbol} Spread Recommendations
        </h2>
        <div className="text-center py-8">
          <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No spread recommendations found for {symbol}
          </p>
          <button
            onClick={onRefresh}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
          >
            Refresh Data
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {symbol} Spread Recommendations
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {recommendations.length} opportunities found • Delta range: 0.15-0.26
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <SortHeader field="type">Type</SortHeader>
              <SortHeader field="buy_strike">Strikes</SortHeader>
              <SortHeader field="delta_difference">Delta Diff</SortHeader>
              <SortHeader field="risk_reward_ratio">Risk:Reward</SortHeader>
              <SortHeader field="profit_per_100_up">P&L/100pts</SortHeader>
              <SortHeader field="total_volume">Volume</SortHeader>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {sortedRecommendations.map((spread, index) => (
              <React.Fragment key={index}>
                <tr className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getSpreadTypeIcon(spread.type)}
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {spread.type.replace(' Spread', '')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      <div>Buy: {spread.buy_strike}</div>
                      <div>Sell: {spread.sell_strike}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      spread.delta_difference >= 0.20 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {formatNumber(spread.delta_difference, 4)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900 dark:text-white">
                      1:{formatNumber(spread.risk_reward_ratio)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">
                      <div className="profit-positive">
                        ↑ {formatCurrency(spread.profit_per_100_up)}
                      </div>
                      <div className="profit-negative">
                        ↓ {formatCurrency(spread.profit_per_100_down)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {(spread.total_volume / 1000000).toFixed(1)}M
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setExpandedRow(expandedRow === index ? null : index)}
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      {expandedRow === index ? 'Hide' : 'Details'}
                    </button>
                  </td>
                </tr>
                
                {/* Expanded Row */}
                {expandedRow === index && (
                  <tr className="bg-gray-50 dark:bg-gray-700">
                    <td colSpan="7" className="px-6 py-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">Buy Leg</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            Strike: {spread.buy_strike}<br/>
                            Delta: {formatNumber(spread.buy_delta, 4)}<br/>
                            Premium: {formatCurrency(spread.buy_premium)}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">Sell Leg</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            Strike: {spread.sell_strike}<br/>
                            Delta: {formatNumber(spread.sell_delta, 4)}<br/>
                            Premium: {formatCurrency(spread.sell_premium)}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">Profit/Loss</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            Max Profit: {formatCurrency(spread.max_profit)}<br/>
                            Max Loss: {formatCurrency(spread.max_loss)}<br/>
                            Breakeven: {spread.breakeven}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">Details</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            Net Premium: {formatCurrency(spread.net_premium)}<br/>
                            Expiry: {spread.expiry}<br/>
                            Prob. Profit: {formatNumber(spread.probability_profit)}%
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default RecommendationsTable