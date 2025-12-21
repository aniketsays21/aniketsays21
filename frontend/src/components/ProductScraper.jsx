import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function ProductScraper({ onComplete }) {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [scrapedProduct, setScrapedProduct] = useState(null)

  const handleScrape = async () => {
    if (!url) {
      toast.error('Please enter a product URL')
      return
    }

    setIsLoading(true)

    try {
      const response = await axios.post('/api/scrape', { url })
      setScrapedProduct(response.data)
      toast.success('Product scraped successfully!')
    } catch (error) {
      console.error('Scraping error:', error)
      toast.error('Failed to scrape product. Please check the URL.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleContinue = () => {
    if (scrapedProduct) {
      onComplete(scrapedProduct)
    } else {
      onComplete(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Product Information</h2>
        <p className="mt-1 text-gray-600">
          Enter a product URL to automatically extract images and description
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product URL (Optional)
          </label>
          <div className="flex space-x-2">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.example.com/product"
              className="input flex-1"
              disabled={isLoading}
            />
            <button
              onClick={handleScrape}
              disabled={isLoading || !url}
              className="btn btn-primary px-8"
            >
              {isLoading ? 'Scraping...' : 'Scrape'}
            </button>
          </div>
        </div>

        {scrapedProduct && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">
              ✓ Product Scraped Successfully
            </h3>
            <div className="space-y-2 text-sm text-green-800">
              <p><strong>Title:</strong> {scrapedProduct.title}</p>
              <p><strong>Images found:</strong> {scrapedProduct.images.length}</p>
              {scrapedProduct.price && (
                <p><strong>Price:</strong> {scrapedProduct.price}</p>
              )}
            </div>
          </div>
        )}

        {/* Display scraped images */}
        {scrapedProduct && scrapedProduct.images && scrapedProduct.images.length > 0 && (
          <div className="mt-6">
            <h3 className="font-semibold text-gray-900 mb-3">Scraped Product Images</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {scrapedProduct.images.map((imageUrl, index) => (
                <div
                  key={index}
                  className="relative aspect-square rounded-lg overflow-hidden border border-gray-200 bg-gray-100"
                >
                  <img
                    src={imageUrl}
                    alt={`Product image ${index + 1}`}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border-t pt-4">
          <button
            onClick={handleContinue}
            className="btn btn-primary w-full"
          >
            {scrapedProduct ? 'Continue with Product' : 'Skip this step'}
          </button>
        </div>
      </div>
    </div>
  )
}
