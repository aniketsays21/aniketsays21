import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function ActionSelector({ selected, onSelect }) {
  const [actions, setActions] = useState([])

  useEffect(() => {
    loadActions()
  }, [])

  const loadActions = async () => {
    try {
      const response = await axios.get('/api/actions')
      setActions(response.data)
    } catch (error) {
      console.error('Error loading actions:', error)
      toast.error('Failed to load actions')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Action</h2>
        <p className="mt-1 text-gray-600">
          Choose the model's action/movement in the video
        </p>
      </div>

      {/* Actions List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {actions.map((action) => (
          <div
            key={action.id}
            onClick={() => onSelect(action)}
            className={`cursor-pointer rounded-lg border-2 p-4 transition-all ${
              selected?.id === action.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-primary-300'
            }`}
          >
            <div className="flex items-start space-x-4">
              {action.preview_url && (
                <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  <img
                    src={action.preview_url}
                    alt={action.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">
                  {action.name}
                </h3>
                {action.description && (
                  <p className="text-sm text-gray-600 mb-2">
                    {action.description}
                  </p>
                )}
                <p className="text-xs text-gray-500">
                  Duration: {action.duration}s
                </p>
              </div>
              {selected?.id === action.id && (
                <div className="text-primary-600 text-xl">✓</div>
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
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900">
            ✓ Selected: <strong>{selected.name}</strong>
          </p>
        </div>
      )}
    </div>
  )
}
