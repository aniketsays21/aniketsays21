export default function VideoPreview({ formData, isGenerating, generatedVideo, onGenerate }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Generate Video</h2>
        <p className="mt-1 text-gray-600">
          Review your settings and generate your UGC video
        </p>
      </div>

      {/* Configuration Summary */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-4">
        <h3 className="font-semibold text-gray-900 text-lg">Configuration Summary</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Model */}
          <div className="flex items-start space-x-3">
            <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
              {formData.model && (
                <img
                  src={formData.model.thumbnail_url || formData.model.file_url}
                  alt="Model"
                  className="w-full h-full object-cover"
                />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Model</p>
              <p className="text-sm text-gray-900">
                {formData.model?.name || 'Not selected'}
              </p>
            </div>
          </div>

          {/* Background */}
          <div className="flex items-start space-x-3">
            <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
              {formData.background && (
                <img
                  src={formData.background.thumbnail_url || formData.background.file_url}
                  alt="Background"
                  className="w-full h-full object-cover"
                />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Background</p>
              <p className="text-sm text-gray-900">
                {formData.background?.name || 'Not selected'}
              </p>
            </div>
          </div>

          {/* Action */}
          <div>
            <p className="text-sm font-medium text-gray-700">Action</p>
            <p className="text-sm text-gray-900">
              {formData.action?.name || 'Not selected'}
            </p>
          </div>

          {/* Voice */}
          <div>
            <p className="text-sm font-medium text-gray-700">Voice Emotion</p>
            <p className="text-sm text-gray-900 capitalize">
              {formData.voice?.emotion || 'Neutral'}
            </p>
          </div>

          {/* Duration */}
          <div>
            <p className="text-sm font-medium text-gray-700">Duration</p>
            <p className="text-sm text-gray-900">{formData.duration} seconds</p>
          </div>

          {/* Product */}
          {formData.product && (
            <div>
              <p className="text-sm font-medium text-gray-700">Product</p>
              <p className="text-sm text-gray-900 truncate">
                {formData.product.title}
              </p>
            </div>
          )}
        </div>

        {/* Script */}
        {formData.voice?.text && (
          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Script</p>
            <p className="text-sm text-gray-900 italic">
              "{formData.voice.text}"
            </p>
          </div>
        )}
      </div>

      {/* Generate Button */}
      {!generatedVideo && (
        <button
          onClick={onGenerate}
          disabled={isGenerating || !formData.model || !formData.background || !formData.action}
          className="btn btn-primary w-full py-4 text-lg"
        >
          {isGenerating ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generating Video... This may take 2-5 minutes
            </span>
          ) : (
            '🎬 Generate Video'
          )}
        </button>
      )}

      {/* Generated Video */}
      {generatedVideo && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="font-semibold text-green-900 text-lg mb-4">
            ✓ Video Generated Successfully!
          </h3>

          <div className="space-y-4">
            {/* Video Player */}
            <div className="bg-black rounded-lg overflow-hidden">
              <video
                src={generatedVideo.output_video_url}
                controls
                className="w-full"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Info */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-700 font-medium">Processing Time</p>
                <p className="text-gray-900">
                  {generatedVideo.processing_time?.toFixed(1)}s
                </p>
              </div>
              <div>
                <p className="text-gray-700 font-medium">Status</p>
                <p className="text-green-700 font-semibold capitalize">
                  {generatedVideo.status}
                </p>
              </div>
            </div>

            {/* Download Button */}
            <a
              href={generatedVideo.output_video_url}
              download
              className="btn btn-primary w-full text-center block"
            >
              ⬇️ Download Video
            </a>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-xl">⚡</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-900">
              Processing Information
            </h3>
            <div className="mt-2 text-sm text-yellow-800">
              <ul className="list-disc list-inside space-y-1">
                <li>Video generation typically takes 2-5 minutes</li>
                <li>Using free AI models (Bark for voice, MagicAnimate for video)</li>
                <li>You'll see progress updates as the video is generated</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
