import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import VideoGenerator from './pages/VideoGenerator'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI UGC Video Platform
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Create professional UGC videos with AI
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                🤖 AI Powered
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <VideoGenerator />
      </main>

      {/* Footer */}
      <footer className="mt-12 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>Built with free/open-source AI models</p>
            <p className="mt-1">
              <span className="font-semibold">Bark</span> for voice •{' '}
              <span className="font-semibold">MagicAnimate</span> for video
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
