import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Option Spreads Analyzer
        </h1>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Welcome!</h2>
          <p className="text-gray-600">
            The application is loading. If you see this message, React is working correctly.
          </p>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800">
              Backend connection will be established once the FastAPI server is running.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App