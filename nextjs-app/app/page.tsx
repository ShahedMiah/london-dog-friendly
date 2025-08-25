'use client'

import { useState } from 'react'

interface ExportStatus {
  isRunning: boolean
  progress: string
  stage: string
  totalVenues: number
  processedVenues: number
  error: string | null
  downloadUrl: string | null
}

export default function HomePage() {
  const [exportStatus, setExportStatus] = useState<ExportStatus>({
    isRunning: false,
    progress: '',
    stage: '',
    totalVenues: 0,
    processedVenues: 0,
    error: null,
    downloadUrl: null
  })

  const startExport = async () => {
    setExportStatus({
      isRunning: true,
      progress: 'Initializing scraper...',
      stage: 'Starting',
      totalVenues: 0,
      processedVenues: 0,
      error: null,
      downloadUrl: null
    })

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(line => line.trim())

          for (const line of lines) {
            try {
              const data = JSON.parse(line)
              setExportStatus(prev => ({
                ...prev,
                ...data
              }))
            } catch (e) {
              // Skip invalid JSON lines
            }
          }
        }
      }
    } catch (error) {
      setExportStatus(prev => ({
        ...prev,
        isRunning: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }))
    }
  }

  const downloadFile = () => {
    if (exportStatus.downloadUrl) {
      const link = document.createElement('a')
      link.href = exportStatus.downloadUrl
      link.download = `london-dog-friendly-venues-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const resetExport = () => {
    setExportStatus({
      isRunning: false,
      progress: '',
      stage: '',
      totalVenues: 0,
      processedVenues: 0,
      error: null,
      downloadUrl: null
    })
  }

  const progressPercentage = exportStatus.totalVenues > 0 
    ? Math.round((exportStatus.processedVenues / exportStatus.totalVenues) * 100)
    : 0

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            🐕 Dog-Friendly Venue Data Export
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            Export comprehensive data of dog-friendly venues across London from BringFido.com
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">121+</div>
              <div className="text-sm text-gray-600">Restaurants</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">658+</div>
              <div className="text-sm text-gray-600">Hotels</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">44+</div>
              <div className="text-sm text-gray-600">Attractions</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">8+</div>
              <div className="text-sm text-gray-600">Services</div>
            </div>
          </div>
        </div>

        {/* Export Controls */}
        <div className="text-center mb-8">
          {!exportStatus.isRunning && !exportStatus.downloadUrl && (
            <button
              onClick={startExport}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors duration-200 text-lg"
            >
              🚀 Start Data Export
            </button>
          )}

          {exportStatus.isRunning && (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="text-lg font-medium text-gray-700">Exporting data...</span>
              </div>
              
              <div className="bg-gray-200 rounded-full h-3 max-w-md mx-auto">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              
              <div className="text-sm text-gray-600">
                {exportStatus.processedVenues} / {exportStatus.totalVenues} venues processed ({progressPercentage}%)
              </div>
            </div>
          )}

          {exportStatus.downloadUrl && (
            <div className="space-y-4">
              <div className="text-green-600 font-medium text-lg">
                ✅ Export completed successfully!
              </div>
              <div className="space-x-4">
                <button
                  onClick={downloadFile}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg transition-colors duration-200 text-lg"
                >
                  📥 Download CSV File
                </button>
                <button
                  onClick={resetExport}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition-colors duration-200"
                >
                  🔄 Export Again
                </button>
              </div>
            </div>
          )}

          {exportStatus.error && (
            <div className="space-y-4">
              <div className="text-red-600 font-medium text-lg">
                ❌ Export failed: {exportStatus.error}
              </div>
              <button
                onClick={resetExport}
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition-colors duration-200"
              >
                🔄 Try Again
              </button>
            </div>
          )}
        </div>

        {/* Status Display */}
        {(exportStatus.progress || exportStatus.stage) && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-700 mb-2">Current Status:</div>
            <div className="text-sm text-gray-600">
              <div><strong>Stage:</strong> {exportStatus.stage}</div>
              <div><strong>Progress:</strong> {exportStatus.progress}</div>
            </div>
          </div>
        )}

        {/* Export Details */}
        <div className="mt-12 bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What you'll get:</h3>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Complete venue information (name, address, phone, website)
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              GPS coordinates for mapping integration
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Dog-friendly specific descriptions and details
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Categorized data (restaurants, hotels, attractions, services)
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              CSV format ready for database import or analysis
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}