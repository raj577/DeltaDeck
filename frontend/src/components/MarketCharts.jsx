import React, { useEffect, useRef } from 'react'
import Plot from 'react-plotly.js'
import LoadingSpinner from './LoadingSpinner'
import { ChartBarIcon } from '@heroicons/react/24/outline'

const MarketCharts = ({ chartData, symbol, loading }) => {
  const plotRef = useRef(null)

  const formatChartData = (data) => {
    if (!data || !data.data || data.data.length === 0) {
      return null
    }

    const timestamps = data.data.map(candle => new Date(candle.timestamp))
    const opens = data.data.map(candle => candle.open)
    const highs = data.data.map(candle => candle.high)
    const lows = data.data.map(candle => candle.low)
    const closes = data.data.map(candle => candle.close)
    const volumes = data.data.map(candle => candle.volume)

    return {
      timestamps,
      opens,
      highs,
      lows,
      closes,
      volumes
    }
  }

  const createPlotData = () => {
    const formattedData = formatChartData(chartData)
    if (!formattedData) return []

    const { timestamps, opens, highs, lows, closes, volumes } = formattedData

    return [
      {
        x: timestamps,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        type: 'candlestick',
        name: symbol,
        increasing: { line: { color: '#10B981' } }, // Green
        decreasing: { line: { color: '#EF4444' } }, // Red
        xaxis: 'x',
        yaxis: 'y'
      },
      {
        x: timestamps,
        y: volumes,
        type: 'bar',
        name: 'Volume',
        marker: { color: 'rgba(59, 130, 246, 0.3)' }, // Blue with transparency
        xaxis: 'x',
        yaxis: 'y2'
      }
    ]
  }

  const plotLayout = {
    title: {
      text: `${symbol} Price Chart (1-Minute)`,
      font: { size: 18, color: '#374151' }
    },
    xaxis: {
      title: 'Time',
      type: 'date',
      rangeslider: { visible: false },
      showgrid: true,
      gridcolor: '#E5E7EB'
    },
    yaxis: {
      title: 'Price (₹)',
      side: 'left',
      showgrid: true,
      gridcolor: '#E5E7EB'
    },
    yaxis2: {
      title: 'Volume',
      side: 'right',
      overlaying: 'y',
      showgrid: false
    },
    plot_bgcolor: 'white',
    paper_bgcolor: 'white',
    font: { family: 'Inter, system-ui, sans-serif' },
    margin: { l: 60, r: 60, t: 60, b: 60 },
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(255, 255, 255, 0.8)'
    },
    hovermode: 'x unified'
  }

  const plotConfig = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: [
      'pan2d',
      'lasso2d',
      'select2d',
      'autoScale2d',
      'hoverClosestCartesian',
      'hoverCompareCartesian',
      'toggleSpikelines'
    ],
    responsive: true
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          {symbol} Price Chart
        </h2>
        <LoadingSpinner message="Loading chart data..." />
      </div>
    )
  }

  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          {symbol} Price Chart
        </h2>
        <div className="text-center py-8">
          <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No chart data available for {symbol}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {symbol} Price Chart
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {chartData.data_points} data points • {chartData.interval} interval
        </p>
      </div>

      <div className="p-4">
        <Plot
          ref={plotRef}
          data={createPlotData()}
          layout={plotLayout}
          config={plotConfig}
          style={{ width: '100%', height: '500px' }}
          useResizeHandler={true}
        />
      </div>

      {/* Chart Statistics */}
      <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {chartData.data && chartData.data.length > 0 && (
            <>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Latest Price</div>
                <div className="text-gray-600 dark:text-gray-400">
                  ₹{chartData.data[chartData.data.length - 1]?.close?.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Day High</div>
                <div className="text-gray-600 dark:text-gray-400">
                  ₹{Math.max(...chartData.data.map(d => d.high)).toFixed(2)}
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Day Low</div>
                <div className="text-gray-600 dark:text-gray-400">
                  ₹{Math.min(...chartData.data.map(d => d.low)).toFixed(2)}
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Volume</div>
                <div className="text-gray-600 dark:text-gray-400">
                  {(chartData.data.reduce((sum, d) => sum + d.volume, 0) / 1000000).toFixed(1)}M
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default MarketCharts