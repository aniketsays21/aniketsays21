import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

// 6 Categories × 3 Options = 18 Preset Backgrounds
const DEFAULT_BACKGROUNDS = [
  // Studio (3)
  {
    id: 'bg-studio-1',
    name: 'White Studio',
    category: 'Studio',
    file_url: 'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-studio-2',
    name: 'Gray Gradient',
    category: 'Studio',
    file_url: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-studio-3',
    name: 'Dark Studio',
    category: 'Studio',
    file_url: 'https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=400&h=300&fit=crop',
    is_preset: true
  },
  // Living Room (3)
  {
    id: 'bg-living-1',
    name: 'Modern Living',
    category: 'Living Room',
    file_url: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-living-2',
    name: 'Cozy Interior',
    category: 'Living Room',
    file_url: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-living-3',
    name: 'Minimalist Space',
    category: 'Living Room',
    file_url: 'https://images.unsplash.com/photo-1598928506311-c55ez1afedee?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1598928506311-c55ez1afedee?w=400&h=300&fit=crop',
    is_preset: true
  },
  // Outdoor (3)
  {
    id: 'bg-outdoor-1',
    name: 'City Street',
    category: 'Outdoor',
    file_url: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-outdoor-2',
    name: 'Nature Park',
    category: 'Outdoor',
    file_url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-outdoor-3',
    name: 'Beach Scene',
    category: 'Outdoor',
    file_url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop',
    is_preset: true
  },
  // Office (3)
  {
    id: 'bg-office-1',
    name: 'Modern Office',
    category: 'Office',
    file_url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-office-2',
    name: 'Home Office',
    category: 'Office',
    file_url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-office-3',
    name: 'Co-working Space',
    category: 'Office',
    file_url: 'https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?w=400&h=300&fit=crop',
    is_preset: true
  },
  // Kitchen (3)
  {
    id: 'bg-kitchen-1',
    name: 'Modern Kitchen',
    category: 'Kitchen',
    file_url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-kitchen-2',
    name: 'Rustic Kitchen',
    category: 'Kitchen',
    file_url: 'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-kitchen-3',
    name: 'Minimalist Counter',
    category: 'Kitchen',
    file_url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=300&fit=crop',
    is_preset: true
  },
  // Abstract (3)
  {
    id: 'bg-abstract-1',
    name: 'Gradient Blur',
    category: 'Abstract',
    file_url: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-abstract-2',
    name: 'Bokeh Lights',
    category: 'Abstract',
    file_url: 'https://images.unsplash.com/photo-1519751138087-5bf79df62d5b?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1519751138087-5bf79df62d5b?w=400&h=300&fit=crop',
    is_preset: true
  },
  {
    id: 'bg-abstract-3',
    name: 'Soft Pastel',
    category: 'Abstract',
    file_url: 'https://images.unsplash.com/photo-1557683316-973673baf926?w=800&h=600&fit=crop',
    thumbnail_url: 'https://images.unsplash.com/photo-1557683316-973673baf926?w=400&h=300&fit=crop',
    is_preset: true
  }
]

// Category icons/emojis
const CATEGORY_ICONS = {
  'Studio': '🎬',
  'Living Room': '🛋️',
  'Outdoor': '🌳',
  'Office': '💼',
  'Kitchen': '🍳',
  'Abstract': '🎨'
}

const CATEGORIES = ['Studio', 'Living Room', 'Outdoor', 'Office', 'Kitchen', 'Abstract']

export default function BackgroundSelector({ selected, onSelect }) {
  const [backgrounds, setBackgrounds] = useState(DEFAULT_BACKGROUNDS)
  const [selectedCategory, setSelectedCategory] = useState(null)

  useEffect(() => {
    loadBackgrounds()
  }, [])

  const loadBackgrounds = async () => {
    try {
      const response = await axios.get('/api/backgrounds')
      // Combine preset backgrounds with any custom uploaded ones
      const customBackgrounds = response.data || []
      setBackgrounds([...DEFAULT_BACKGROUNDS, ...customBackgrounds])
    } catch (error) {
      console.error('Error loading backgrounds:', error)
      // Keep default backgrounds even if API fails
      setBackgrounds(DEFAULT_BACKGROUNDS)
    }
  }

  // Filter backgrounds by category
  const filteredBackgrounds = selectedCategory
    ? backgrounds.filter(bg => bg.category === selectedCategory)
    : backgrounds

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Background</h2>
        <p className="mt-1 text-gray-600">
          Choose a background for your UGC video ({filteredBackgrounds.length} available)
        </p>
      </div>

      {/* Category Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Filter by Category
        </label>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              selectedCategory === null
                ? 'bg-primary-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({backgrounds.length})
          </button>
          {CATEGORIES.map((category) => {
            const count = backgrounds.filter(bg => bg.category === category).length
            return (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedCategory === category
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {CATEGORY_ICONS[category]} {category} ({count})
              </button>
            )
          })}
        </div>
      </div>

      {/* Background Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {filteredBackgrounds.map((background) => (
          <div
            key={background.id}
            onClick={() => onSelect(background)}
            className={`cursor-pointer rounded-lg border-2 overflow-hidden transition-all hover:scale-102 ${
              selected?.id === background.id
                ? 'border-primary-500 ring-2 ring-primary-200 scale-105'
                : 'border-gray-200 hover:border-primary-300'
            }`}
          >
            <div className="aspect-video bg-gray-100 relative">
              <img
                src={background.thumbnail_url || background.file_url}
                alt={background.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/400x300?text=Image+Not+Found'
                }}
              />
              {selected?.id === background.id && (
                <div className="absolute top-2 right-2 bg-primary-500 text-white rounded-full p-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
              {background.category && (
                <div className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full">
                  {CATEGORY_ICONS[background.category]} {background.category}
                </div>
              )}
            </div>
            <div className="p-3">
              <p className="text-sm font-medium text-gray-900 truncate">
                {background.name}
              </p>
            </div>
          </div>
        ))}
      </div>

      {filteredBackgrounds.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No backgrounds in this category.</p>
          <p className="text-sm mt-2">Try selecting a different category.</p>
        </div>
      )}

      {selected && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <img
            src={selected.thumbnail_url || selected.file_url}
            alt={selected.name}
            className="w-16 h-12 object-cover rounded"
          />
          <div>
            <p className="text-sm text-green-900">
              Selected: <strong>{selected.name}</strong>
            </p>
            <p className="text-xs text-green-700">{selected.category}</p>
          </div>
        </div>
      )}
    </div>
  )
}
