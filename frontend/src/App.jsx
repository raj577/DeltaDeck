import React, { useState, useEffect, useRef } from 'react'
import { apiService } from './services/apiService'

function App() {
  const [currentPrices, setCurrentPrices] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedSymbol, setSelectedSymbol] = useState('NIFTY')
  const [lastUpdated, setLastUpdated] = useState(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [wsError, setWsError] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  // Fetch initial data and setup WebSocket
  useEffect(() => {
    fetchInitialData()
    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  const fetchInitialData = async () => {
    try {
      setError(null)
      console.log('Fetching initial data from backend...')

      // Test basic connectivity first
      console.log('Testing API connectivity...')
      const response = await fetch('http://127.0.0.1:8000/api/prices')
      console.log('Response status:', response.status)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Initial price data:', data)

      setCurrentPrices(data.prices)
      setLastUpdated(new Date())
      setLoading(false)
      console.log('Initial data fetched successfully')

    } catch (err) {
      console.error('Error fetching initial data:', err)
      console.error('Error details:', err.message)
      setError(err.message || 'Failed to fetch initial data from backend server.')

      // Set mock data for development when backend is not available
      console.log('Setting mock data...')
      setCurrentPrices({
        NIFTY: { ltp: 25111.45 },
        BANKNIFTY: { ltp: 56828.80 }
      })
      setLastUpdated(new Date())
      setLoading(false)
    }
  }

  // WebSocket connection function
  const connectWebSocket = () => {
    try {
      console.log('🔌 Connecting to WebSocket...')
      const ws = new WebSocket('ws://127.0.0.1:8000/ws')
      wsRef.current = ws

      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        setWsConnected(true)
        setWsError(null)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('📡 Received WebSocket message:', message)
          
          if (message.type === 'price_update' && message.data) {
            setCurrentPrices(message.data)
            setLastUpdated(new Date())
            console.log('💰 Prices updated via WebSocket:', message.data)
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason)
        setWsConnected(false)
        
        // Attempt to reconnect after 3 seconds
        if (!event.wasClean) {
          setWsError('Connection lost. Attempting to reconnect...')
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 Attempting to reconnect WebSocket...')
            connectWebSocket()
          }, 3000)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setWsError('WebSocket connection error')
        setWsConnected(false)
      }

    } catch (error) {
      console.error('❌ Failed to create WebSocket connection:', error)
      setWsError('Failed to connect to real-time feed')
    }
  }



  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol)
    setLoading(true)
  }

  const handleRefresh = () => {
    fetchInitialData()
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  if (loading && !currentPrices) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading market data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-blue-600 rounded flex items-center justify-center">
                <span className="text-white font-bold">📊</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Option Spreads Analyzer
                </h1>
                <p className="text-sm text-gray-500">
                  Real-time NIFTY & BANKNIFTY spread recommendations
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Symbol:</label>
                <select
                  value={selectedSymbol}
                  onChange={(e) => handleSymbolChange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="NIFTY">NIFTY</option>
                  <option value="BANKNIFTY">BANKNIFTY</option>
                </select>
              </div>

              <button
                onClick={handleRefresh}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
              >
                <span>🔄</span>
                <span>Refresh</span>
              </button>

              {/* WebSocket Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-xs text-gray-500">
                  {wsConnected ? 'Live' : 'Offline'}
                </span>
              </div>

              <div className="text-xs text-gray-500">
                <div>Last updated:</div>
                <div>{lastUpdated?.toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <span className="text-red-400 mr-3">⚠️</span>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-800">
                  Error Loading Data
                </h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button
                  onClick={handleRefresh}
                  className="mt-3 flex items-center space-x-2 text-sm text-red-800 hover:text-red-900 font-medium"
                >
                  <span>🔄</span>
                  <span>Try Again</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Current Prices Section */}
        {currentPrices && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className={`p-6 rounded-lg border-2 transition-all ${selectedSymbol === 'NIFTY'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white'
              }`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className={`text-lg font-semibold ${selectedSymbol === 'NIFTY' ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                    NIFTY
                  </h3>
                  <p className="text-sm text-gray-500">NIFTY 50 Index</p>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${selectedSymbol === 'NIFTY' ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                    {formatPrice(currentPrices?.NIFTY?.ltp || 0)}
                  </div>
                  <div className="flex items-center text-sm text-green-600">
                    <span className="mr-1">📈</span>
                    <span>Live</span>
                  </div>
                </div>
              </div>
            </div>

            <div className={`p-6 rounded-lg border-2 transition-all ${selectedSymbol === 'BANKNIFTY'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white'
              }`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className={`text-lg font-semibold ${selectedSymbol === 'BANKNIFTY' ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                    BANKNIFTY
                  </h3>
                  <p className="text-sm text-gray-500">BANK NIFTY Index</p>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${selectedSymbol === 'BANKNIFTY' ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                    {formatPrice(currentPrices?.BANKNIFTY?.ltp || 0)}
                  </div>
                  <div className="flex items-center text-sm text-green-600">
                    <span className="mr-1">📈</span>
                    <span>Live</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recommendations Section */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {selectedSymbol} Spread Recommendations
            </h2>
            <div className="text-center py-8">
              <span className="text-4xl mb-4 block">📊</span>
              <p className="text-gray-500">
                No spread recommendations found for {selectedSymbol}
              </p>
              <button
                onClick={handleRefresh}
                className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
              >
                Refresh Data
              </button>
            </div>
          </div>

          {/* Charts Section */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {selectedSymbol} Price Chart
            </h2>
            <div className="text-center py-8">
              <span className="text-4xl mb-4 block">📈</span>
              <p className="text-gray-500">
                No chart data available for {selectedSymbol}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App