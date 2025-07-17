import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'https://option-spreads-api.onrender.com',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)

    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      throw new Error(data.message || data.detail || `Server error: ${status}`)
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error: Unable to connect to server')
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred')
    }
  }
)

// Retry logic for failed requests
const retryRequest = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      if (attempt === maxRetries) {
        throw error
      }
      console.warn(`Request failed (attempt ${attempt}/${maxRetries}), retrying in ${delay}ms...`)
      await new Promise(resolve => setTimeout(resolve, delay))
      delay *= 2 // Exponential backoff
    }
  }
}

export const apiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/health')
    return response.data
  },

  // API status
  async getApiStatus() {
    const response = await api.get('/api/status')
    return response.data
  },

  // Current prices
  async fetchCurrentPrices() {
    return retryRequest(async () => {
      const response = await api.get('/api/prices')
      return response.data
    })
  },

  // Spread recommendations
  async fetchRecommendations(symbol = 'NIFTY', strikesRange = 6) {
    return retryRequest(async () => {
      const response = await api.post('/api/recommendations', {
        symbol: symbol.toUpperCase(),
        strikes_range: strikesRange
      })
      return response.data
    })
  },

  // Quick recommendations (GET endpoint)
  async fetchQuickRecommendations(symbol = 'NIFTY') {
    return retryRequest(async () => {
      const response = await api.get(`/api/recommendations/${symbol.toUpperCase()}`)
      return response.data
    })
  },

  // Chart data
  async fetchChartData(symbol = 'NIFTY', interval = 'ONE_MINUTE', fromDate = null, toDate = null) {
    return retryRequest(async () => {
      const params = {
        symbol: symbol.toUpperCase(),
        interval
      }

      if (fromDate) params.from_date = fromDate
      if (toDate) params.to_date = toDate

      const response = await api.get('/api/chart-data', { params })
      return response.data
    })
  },

  // Top gainers/losers
  async fetchGainersLosers(dataType = 'PercOIGainers', expiryType = 'NEAR') {
    return retryRequest(async () => {
      const response = await api.get('/api/gainers-losers', {
        params: {
          data_type: dataType,
          expiry_type: expiryType
        }
      })
      return response.data
    })
  },

  // WebSocket info
  async getWebSocketInfo() {
    const response = await api.get('/api/websocket-info')
    return response.data
  }
}

// Export individual functions for convenience
export const {
  checkHealth,
  getApiStatus,
  fetchCurrentPrices,
  fetchRecommendations,
  fetchQuickRecommendations,
  fetchChartData,
  fetchGainersLosers,
  getWebSocketInfo
} = apiService

export default apiService