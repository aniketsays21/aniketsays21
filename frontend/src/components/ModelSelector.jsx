import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'

// Default preset models (Indian men and women)
const DEFAULT_MODELS = [
  {
    id: 'preset-1',
    name: 'Priya',
    gender: 'female',
    file_url: 'https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-2',
    name: 'Arjun',
    gender: 'male',
    file_url: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-3',
    name: 'Ananya',
    gender: 'female',
    file_url: 'https://images.unsplash.com/photo-1618568949778-d07c04cb66a8?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1618568949778-d07c04cb66a8?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-4',
    name: 'Rahul',
    gender: 'male',
    file_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-5',
    name: 'Neha',
    gender: 'female',
    file_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-6',
    name: 'Vikram',
    gender: 'male',
    file_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  },
  {
    id: 'preset-7',
    name: 'Kavya',
    gender: 'female',
    file_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    thumbnail_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face',
    is_preset: true
  }
]

export default function ModelSelector({ selected, onSelect }) {
  const [models, setModels] = useState(DEFAULT_MODELS)
  const [isUploading, setIsUploading] = useState(false)
  const [filter, setFilter] = useState('all') // 'all', 'male', 'female'

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const response = await axios.get('/api/models')
      // Combine preset models with any uploaded models from backend
      const uploadedModels = response.data || []
      setModels([...DEFAULT_MODELS, ...uploadedModels])
    } catch (error) {
      console.error('Error loading models:', error)
      // Keep default models even if API fails
      setModels(DEFAULT_MODELS)
    }
  }

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', file.name)

      const response = await axios.post('/api/upload-model', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setModels([...models, response.data])
      onSelect(response.data)
      toast.success('Model uploaded successfully!')
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload model image')
    } finally {
      setIsUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Model</h2>
        <p className="mt-1 text-gray-600">
          Choose a model image or upload your own
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <div className="text-4xl">📤</div>
          <p className="text-lg font-medium text-gray-900">
            {isDragActive ? 'Drop the image here' : 'Upload Model Image'}
          </p>
          <p className="text-sm text-gray-600">
            Drag & drop or click to select
          </p>
        </div>
      </div>

      {/* Gender Filter */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Models
        </button>
        <button
          onClick={() => setFilter('female')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            filter === 'female'
              ? 'bg-pink-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          👩 Female
        </button>
        <button
          onClick={() => setFilter('male')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            filter === 'male'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          👨 Male
        </button>
      </div>

      {/* Model Grid */}
      {models.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Choose a Model</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {models
              .filter(model => filter === 'all' || model.gender === filter)
              .map((model) => (
              <div
                key={model.id}
                onClick={() => onSelect(model)}
                className={`cursor-pointer rounded-lg border-2 overflow-hidden transition-all ${
                  selected?.id === model.id
                    ? 'border-primary-500 ring-2 ring-primary-200 scale-105'
                    : 'border-gray-200 hover:border-primary-300 hover:scale-102'
                }`}
              >
                <div className="aspect-square bg-gray-100 relative">
                  <img
                    src={model.thumbnail_url || model.file_url}
                    alt={model.name}
                    className="w-full h-full object-cover"
                  />
                  {selected?.id === model.id && (
                    <div className="absolute top-2 right-2 bg-primary-500 text-white rounded-full p-1">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                  {model.gender && (
                    <div className={`absolute bottom-2 left-2 text-xs px-2 py-1 rounded-full ${
                      model.gender === 'female' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {model.gender === 'female' ? '👩' : '👨'}
                    </div>
                  )}
                </div>
                <div className="p-2">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {model.name}
                  </p>
                </div>
              </div>
            ))}
          </div>
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
