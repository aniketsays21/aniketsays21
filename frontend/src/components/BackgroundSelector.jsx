import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function BackgroundSelector({ selected, onSelect }) {
  const [backgrounds, setBackgrounds] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)

  useEffect(() => {
    loadBackgrounds()
  }, [selectedCategory])

  const loadBackgrounds = async () => {
    try {
      const params = selectedCategory ? { category: selectedCategory } : {}
      const response = await axios.get('/api/backgrounds', { params })
      setBackgrounds(response.data)

      // Extract unique categories
      const uniqueCategories = [...new Set(response.data.map(bg => bg.category).filter(Boolean))]
      setCategories(uniqueCategories)
    } catch (error) {
      console.error('Error loading backgrounds:', error)
      toast.error('Failed to load backgrounds')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Background</h2>
        <p className="mt-1 text-gray-600">
          Choose a background for your UGC video
        </p>
      </div>

      {/* Category Filter */}
      {categories.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === null
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Background Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {backgrounds.map((background) => (
          <div
            key={background.id}
            onClick={() => onSelect(background)}
            className={`cursor-pointer rounded-lg border-2 overflow-hidden transition-all ${
              selected?.id === background.id
                ? 'border-primary-500 ring-2 ring-primary-200'
                : 'border-gray-200 hover:border-primary-300'
            }`}
          >
            <div className="aspect-video bg-gray-100">
              <img
                src={background.thumbnail_url || background.file_url}
                alt={background.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="p-3">
              <p className="text-sm font-medium text-gray-900 truncate">
                {background.name}
              </p>
              {background.category && (
                <p className="text-xs text-gray-500">{background.category}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {backgrounds.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No backgrounds available.</p>
          <p className="text-sm mt-2">Upload backgrounds using the API.</p>
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
