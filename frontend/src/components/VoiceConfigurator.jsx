import { useState } from 'react'

const EMOTIONS = [
  { value: 'neutral', label: 'Neutral', emoji: '😐' },
  { value: 'happy', label: 'Happy', emoji: '😊' },
  { value: 'excited', label: 'Excited', emoji: '🤩' },
  { value: 'calm', label: 'Calm', emoji: '😌' },
  { value: 'sad', label: 'Sad', emoji: '😢' },
  { value: 'angry', label: 'Angry', emoji: '😠' },
  { value: 'surprised', label: 'Surprised', emoji: '😮' },
]

export default function VoiceConfigurator({ value, onChange, duration, onDurationChange }) {
  const handleTextChange = (text) => {
    onChange({ ...value, text })
  }

  const handleEmotionChange = (emotion) => {
    onChange({ ...value, emotion })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Configure Voice</h2>
        <p className="mt-1 text-gray-600">
          Set up the audio for your UGC video
        </p>
      </div>

      {/* Audio Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Script / Text to Speech
        </label>
        <textarea
          value={value.text}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Enter the text you want the model to say... e.g., 'This product is amazing! You're going to love it.'"
          rows={4}
          className="input resize-none"
        />
        <p className="mt-1 text-sm text-gray-500">
          {value.text.length} characters
        </p>
      </div>

      {/* Emotion Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Voice Emotion
        </label>
        <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
          {EMOTIONS.map((emotion) => (
            <button
              key={emotion.value}
              onClick={() => handleEmotionChange(emotion.value)}
              className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                value.emotion === emotion.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
              }`}
            >
              <span className="text-3xl mb-1">{emotion.emoji}</span>
              <span className="text-xs font-medium text-gray-700">
                {emotion.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Duration */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Video Duration: {duration} seconds
        </label>
        <input
          type="range"
          min="3"
          max="30"
          step="1"
          value={duration}
          onChange={(e) => onDurationChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>3s</span>
          <span>30s</span>
        </div>
      </div>

      {/* Preview */}
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-2">Preview</h3>
        <div className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Emotion:</strong>{' '}
            {EMOTIONS.find(e => e.value === value.emotion)?.label}
          </p>
          <p>
            <strong>Duration:</strong> {duration}s
          </p>
          {value.text && (
            <div>
              <strong>Script:</strong>
              <p className="mt-1 italic text-gray-600">"{value.text}"</p>
            </div>
          )}
        </div>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-xl">ℹ️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-900">
              Voice Synthesis Info
            </h3>
            <div className="mt-2 text-sm text-blue-800">
              <p>
                We use <strong>Bark AI</strong> - a free, open-source voice synthesis model
                that supports emotional speech and natural intonation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
