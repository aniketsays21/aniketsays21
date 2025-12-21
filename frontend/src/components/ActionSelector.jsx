import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

// Default preset actions for UGC videos
const DEFAULT_ACTIONS = [
  {
    id: 'action-talking',
    name: 'Talking',
    description: 'Natural talking animation with subtle head and hand movements',
    icon: '🗣️',
    duration: 5,
    category: 'Speaking',
    pose_sequence: { type: 'talking', intensity: 'medium' },
    is_preset: true
  },
  {
    id: 'action-presenting',
    name: 'Presenting Product',
    description: 'Gesturing towards product with enthusiastic presentation style',
    icon: '👆',
    duration: 5,
    category: 'Product',
    pose_sequence: { type: 'presenting', intensity: 'medium' },
    is_preset: true
  },
  {
    id: 'action-waving',
    name: 'Waving Hello',
    description: 'Friendly wave greeting animation',
    icon: '👋',
    duration: 3,
    category: 'Greeting',
    pose_sequence: { type: 'waving', intensity: 'high' },
    is_preset: true
  },
  {
    id: 'action-nodding',
    name: 'Nodding',
    description: 'Agreeable nodding motion with slight smile',
    icon: '😊',
    duration: 3,
    category: 'Expression',
    pose_sequence: { type: 'nodding', intensity: 'low' },
    is_preset: true
  },
  {
    id: 'action-thinking',
    name: 'Thinking',
    description: 'Contemplative pose with hand on chin',
    icon: '🤔',
    duration: 4,
    category: 'Expression',
    pose_sequence: { type: 'thinking', intensity: 'low' },
    is_preset: true
  },
  {
    id: 'action-excited',
    name: 'Excited Reaction',
    description: 'Energetic and excited reaction with expressive gestures',
    icon: '🎉',
    duration: 4,
    category: 'Expression',
    pose_sequence: { type: 'excited', intensity: 'high' },
    is_preset: true
  },
  {
    id: 'action-unboxing',
    name: 'Unboxing',
    description: 'Simulated unboxing motion revealing product',
    icon: '📦',
    duration: 6,
    category: 'Product',
    pose_sequence: { type: 'unboxing', intensity: 'medium' },
    is_preset: true
  },
  {
    id: 'action-thumbsup',
    name: 'Thumbs Up',
    description: 'Positive thumbs up gesture with smile',
    icon: '👍',
    duration: 3,
    category: 'Gesture',
    pose_sequence: { type: 'thumbsup', intensity: 'medium' },
    is_preset: true
  }
]

export default function ActionSelector({ selected, onSelect }) {
  const [actions, setActions] = useState(DEFAULT_ACTIONS)

  useEffect(() => {
    loadActions()
  }, [])

  const loadActions = async () => {
    try {
      const response = await axios.get('/api/actions')
      // Combine preset actions with any custom ones
      const customActions = response.data || []
      setActions([...DEFAULT_ACTIONS, ...customActions])
    } catch (error) {
      console.error('Error loading actions:', error)
      // Keep default actions even if API fails
      setActions(DEFAULT_ACTIONS)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Action</h2>
        <p className="mt-1 text-gray-600">
          Choose the model's action/movement in the video ({actions.length} available)
        </p>
      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {actions.map((action) => (
          <div
            key={action.id}
            onClick={() => onSelect(action)}
            className={`cursor-pointer rounded-xl border-2 p-4 transition-all hover:scale-102 ${
              selected?.id === action.id
                ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200 scale-105'
                : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
            }`}
          >
            <div className="text-center">
              {/* Icon */}
              <div className="text-4xl mb-3">
                {action.icon || '🎬'}
              </div>

              {/* Name */}
              <h3 className="font-semibold text-gray-900 mb-1 text-sm">
                {action.name}
              </h3>

              {/* Description */}
              {action.description && (
                <p className="text-xs text-gray-500 mb-2 line-clamp-2">
                  {action.description}
                </p>
              )}

              {/* Duration badge */}
              <span className="inline-block px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-600">
                {action.duration}s
              </span>

              {/* Selected indicator */}
              {selected?.id === action.id && (
                <div className="mt-2 text-primary-600 text-sm font-medium">
                  Selected
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {actions.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No actions available.</p>
          <p className="text-sm mt-2">
            Actions need to be configured in the database.
          </p>
        </div>
      )}

      {selected && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <span className="text-3xl">{selected.icon}</span>
          <div>
            <p className="text-sm text-green-900">
              Selected: <strong>{selected.name}</strong>
            </p>
            <p className="text-xs text-green-700">{selected.description}</p>
          </div>
        </div>
      )}
    </div>
  )
}
