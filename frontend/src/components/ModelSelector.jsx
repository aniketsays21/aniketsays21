import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'

export default function ModelSelector({ selected, onSelect }) {
  const [models, setModels] = useState([])
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const response = await axios.get('/api/models')
      setModels(response.data)
    } catch (error) {
      console.error('Error loading models:', error)
      toast.error('Failed to load models')
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

      {/* Model Grid */}
      {models.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Available Models</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {models.map((model) => (
              <div
                key={model.id}
                onClick={() => onSelect(model)}
                className={`cursor-pointer rounded-lg border-2 overflow-hidden transition-all ${
                  selected?.id === model.id
                    ? 'border-primary-500 ring-2 ring-primary-200'
                    : 'border-gray-200 hover:border-primary-300'
                }`}
              >
                <div className="aspect-square bg-gray-100">
                  <img
                    src={model.thumbnail_url || model.file_url}
                    alt={model.name}
                    className="w-full h-full object-cover"
                  />
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
