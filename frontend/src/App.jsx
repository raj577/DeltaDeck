import React, { useState, useEffect, useRef } from 'react'
import { apiService } from './services/apiService'
import SpreadCards from './components/SpreadCards'
import GeminiChat from './components/GeminiChat'

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

      // Fetch recommendations for the selected symbol
      await fetchRecommendations(selectedSymbol)

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

  const fetchRecommendations = async (symbol) => {
    try {
      console.log(`Fetching recommendations for ${symbol}...`)
      const response = await fetch(`http://127.0.0.1:8000/api/recommendations/${symbol}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const recommendationsData = await response.json()
      console.log('Recommendations fetched:', recommendationsData)
      setRecommendations(recommendationsData)

    } catch (err) {
      console.error('Error fetching recommendations:', err)
      setRecommendations([])
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



  const handleSymbolChange = async (symbol) => {
    setSelectedSymbol(symbol)
    setLoading(true)

    // Fetch recommendations for the new symbol
    await fetchRecommendations(symbol)
    setLoading(false)
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">📊</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  DeltaDeck
                </h1>
                <p className="text-sm text-gray-600 font-medium">
                  Real-time NIFTY & BANKNIFTY spread recommendations
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3 bg-white/60 rounded-lg px-3 py-2 backdrop-blur-sm">
                <label className="text-sm font-semibold text-gray-700">Symbol:</label>
                <select
                  value={selectedSymbol}
                  onChange={(e) => handleSymbolChange(e.target.value)}
                  className="px-3 py-2 border-0 bg-white/80 rounded-lg text-sm font-semibold text-gray-900 focus:ring-2 focus:ring-blue-500 shadow-sm"
                >
                  <option value="NIFTY">NIFTY</option>
                  <option value="BANKNIFTY">BANKNIFTY</option>
                </select>
              </div>

              <button
                onClick={handleRefresh}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg text-sm font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <span className="text-lg">🔄</span>
                <span>Refresh</span>
              </button>

              {/* WebSocket Status */}
              <div className="flex items-center space-x-2 bg-white/60 rounded-lg px-3 py-2 backdrop-blur-sm">
                <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'} shadow-sm`}></div>
                <span className={`text-xs font-semibold ${wsConnected ? 'text-green-700' : 'text-red-700'}`}>
                  {wsConnected ? 'Live' : 'Offline'}
                </span>
              </div>

              <div className="text-xs text-gray-600 bg-white/60 rounded-lg px-3 py-2 backdrop-blur-sm">
                <div className="font-medium">Last updated:</div>
                <div className="font-semibold">{lastUpdated?.toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Developer Credit */}
      <div className="bg-white/60 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
            <span>Developed by Rajat Srivastav</span>
            <span className="text-gray-400">|</span>
            <a 
              href="https://www.linkedin.com/in/rajat-srivastav-393725325/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-semibold transition-colors duration-200"
            >
              <span>Connect me on LinkedIn</span>
              <svg 
                className="w-4 h-4" 
                fill="currentColor" 
                viewBox="0 0 24 24"
              >
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </a>
          </div>
        </div>
      </div>

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
            <div className={`group p-6 rounded-2xl border-2 transition-all duration-300 hover:shadow-xl hover:scale-105 ${selectedSymbol === 'NIFTY'
              ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-blue-100 shadow-lg'
              : 'border-gray-200 bg-gradient-to-br from-white to-gray-50 hover:border-blue-300'
              }`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className={`text-xl font-bold ${selectedSymbol === 'NIFTY' ? 'text-blue-900' : 'text-gray-900'
                      }`}>
                      NIFTY
                    </h3>
                    {selectedSymbol === 'NIFTY' && (
                      <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs font-semibold rounded-full">
                        SELECTED
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 font-medium">NIFTY 50 Index</p>
                </div>
                <div className="text-right">
                  <div className={`text-3xl font-bold mb-1 ${selectedSymbol === 'NIFTY' ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                    {formatPrice(currentPrices?.NIFTY?.ltp || 0)}
                  </div>
                  <div className="flex items-center justify-end space-x-1 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-700 font-semibold">Live</span>
                  </div>
                </div>
              </div>
            </div>

            <div className={`group p-6 rounded-2xl border-2 transition-all duration-300 hover:shadow-xl hover:scale-105 ${selectedSymbol === 'BANKNIFTY'
              ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg'
              : 'border-gray-200 bg-gradient-to-br from-white to-gray-50 hover:border-purple-300'
              }`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className={`text-xl font-bold ${selectedSymbol === 'BANKNIFTY' ? 'text-purple-900' : 'text-gray-900'
                      }`}>
                      BANKNIFTY
                    </h3>
                    {selectedSymbol === 'BANKNIFTY' && (
                      <span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs font-semibold rounded-full">
                        SELECTED
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 font-medium">BANK NIFTY Index</p>
                </div>
                <div className="text-right">
                  <div className={`text-3xl font-bold mb-1 ${selectedSymbol === 'BANKNIFTY' ? 'text-purple-900' : 'text-gray-900'
                    }`}>
                    {formatPrice(currentPrices?.BANKNIFTY?.ltp || 0)}
                  </div>
                  <div className="flex items-center justify-end space-x-1 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-700 font-semibold">Live</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recommendations Section */}
          <div className="lg:col-span-1">
            <SpreadCards
              recommendations={recommendations}
              symbol={selectedSymbol}
              loading={loading}
              onRefresh={handleRefresh}
            />
          </div>

          {/* AI Chat Section */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
            <GeminiChat />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App