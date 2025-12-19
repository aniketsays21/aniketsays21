import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import axios from 'axios'

// Import components
import ProductScraper from '../components/ProductScraper'
import ModelSelector from '../components/ModelSelector'
import BackgroundSelector from '../components/BackgroundSelector'
import ActionSelector from '../components/ActionSelector'
import VoiceConfigurator from '../components/VoiceConfigurator'
import VideoPreview from '../components/VideoPreview'

const STEPS = [
  { id: 1, name: 'Product', description: 'Scrape product info' },
  { id: 2, name: 'Model', description: 'Select/upload model' },
  { id: 3, name: 'Background', description: 'Choose background' },
  { id: 4, name: 'Action', description: 'Select model action' },
  { id: 5, name: 'Voice', description: 'Configure audio' },
  { id: 6, name: 'Generate', description: 'Create video' },
]

export default function VideoGenerator() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    product: null,
    model: null,
    background: null,
    action: null,
    voice: {
      text: '',
      emotion: 'neutral',
      voiceId: null,
    },
    duration: 5,
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVideo, setGeneratedVideo] = useState(null)

  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const goToNextStep = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const generateVideo = async () => {
    // Validate all required fields
    if (!formData.model || !formData.background || !formData.action) {
      toast.error('Please complete all required steps')
      return
    }

    setIsGenerating(true)

    try {
      // Create video generation request
      const response = await axios.post('/api/generate', {
        product_id: formData.product?.id || null,
        model_image_id: formData.model.id,
        background_id: formData.background.id,
        action_id: formData.action.id,
        audio_text: formData.voice.text || null,
        emotion: formData.voice.emotion,
        duration: formData.duration,
      })

      const jobId = response.data.job_id

      toast.success('Video generation started!')

      // Poll for job status
      pollJobStatus(jobId)

    } catch (error) {
      console.error('Error generating video:', error)
      toast.error('Failed to start video generation')
      setIsGenerating(false)
    }
  }

  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/video/${jobId}`)
        const job = response.data

        if (job.status === 'completed') {
          clearInterval(interval)
          setGeneratedVideo(job)
          setIsGenerating(false)
          toast.success('Video generated successfully!')
        } else if (job.status === 'failed') {
          clearInterval(interval)
          setIsGenerating(false)
          toast.error(`Video generation failed: ${job.error_message}`)
        } else {
          // Update progress
          const progress = Math.round(job.progress * 100)
          console.log(`Progress: ${progress}%`)
        }
      } catch (error) {
        console.error('Error polling job status:', error)
        clearInterval(interval)
        setIsGenerating(false)
        toast.error('Failed to check video status')
      }
    }, 3000) // Poll every 3 seconds
  }

  return (
    <div className="space-y-8">
      {/* Progress Steps */}
      <div className="card">
        <div className="flex items-center justify-between">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`step-indicator ${
                    currentStep === step.id
                      ? 'active'
                      : currentStep > step.id
                      ? 'completed'
                      : ''
                  }`}
                >
                  {currentStep > step.id ? '✓' : step.id}
                </div>
                <div className="mt-2 text-center">
                  <p className="text-sm font-medium text-gray-900">{step.name}</p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </div>
              {index < STEPS.length - 1 && (
                <div className="w-16 h-1 bg-gray-200 mx-4 mt-[-40px]">
                  <div
                    className={`h-full transition-all ${
                      currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="card min-h-[400px]">
        {currentStep === 1 && (
          <ProductScraper
            onComplete={(product) => {
              updateFormData('product', product)
              goToNextStep()
            }}
          />
        )}

        {currentStep === 2 && (
          <ModelSelector
            selected={formData.model}
            onSelect={(model) => updateFormData('model', model)}
          />
        )}

        {currentStep === 3 && (
          <BackgroundSelector
            selected={formData.background}
            onSelect={(background) => updateFormData('background', background)}
          />
        )}

        {currentStep === 4 && (
          <ActionSelector
            selected={formData.action}
            onSelect={(action) => updateFormData('action', action)}
          />
        )}

        {currentStep === 5 && (
          <VoiceConfigurator
            value={formData.voice}
            onChange={(voice) => updateFormData('voice', voice)}
            duration={formData.duration}
            onDurationChange={(duration) => updateFormData('duration', duration)}
          />
        )}

        {currentStep === 6 && (
          <VideoPreview
            formData={formData}
            isGenerating={isGenerating}
            generatedVideo={generatedVideo}
            onGenerate={generateVideo}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={goToPreviousStep}
          disabled={currentStep === 1}
          className="btn btn-secondary disabled:opacity-50"
        >
          ← Previous
        </button>

        {currentStep < STEPS.length ? (
          <button
            onClick={goToNextStep}
            disabled={
              (currentStep === 2 && !formData.model) ||
              (currentStep === 3 && !formData.background) ||
              (currentStep === 4 && !formData.action)
            }
            className="btn btn-primary"
          >
            Next →
          </button>
        ) : null}
      </div>
    </div>
  )
}
