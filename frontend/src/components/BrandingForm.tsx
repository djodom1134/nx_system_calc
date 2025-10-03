/**
 * OEM Branding and Customization Form Component
 */

import { useState, useRef } from 'react'
import { useCalculatorStore } from '../stores/calculatorStore'

interface BrandingColors {
  primary_color: string
  secondary_color: string
  accent_color: string
}

interface BrandingConfig {
  company_name?: string
  logo_filename?: string
  logo_url?: string
  colors?: BrandingColors
  tagline?: string
  website?: string
}

export default function BrandingForm() {
  const { project, setProject, branding, setBranding } = useCalculatorStore()
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [colors, setColors] = useState<BrandingColors>({
    primary_color: branding?.colors?.primary_color || '#2563eb',
    secondary_color: branding?.colors?.secondary_color || '#3b82f6',
    accent_color: branding?.colors?.accent_color || '#1e40af',
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/svg+xml']
    if (!validTypes.includes(file.type)) {
      setUploadError('Invalid file type. Please upload JPG, PNG, GIF, or SVG.')
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File too large. Maximum size is 5MB.')
      return
    }

    setLogoFile(file)
    setUploadError(null)

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setLogoPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleUpload = async () => {
    if (!logoFile) return

    setIsUploading(true)
    setUploadError(null)

    try {
      const formData = new FormData()
      formData.append('file', logoFile)

      const response = await fetch('http://localhost:8000/api/v1/branding/upload-logo', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const data = await response.json()
      
      // Update branding config
      setBranding({
        ...branding,
        logo_filename: data.filename,
        logo_url: `http://localhost:8000${data.file_path}`,
      })

      setUploadError(null)
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveLogo = () => {
    setLogoFile(null)
    setLogoPreview(null)
    setBranding({
      ...branding,
      logo_filename: undefined,
      logo_url: undefined,
    })
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleColorChange = (colorType: keyof BrandingColors, value: string) => {
    const newColors = { ...colors, [colorType]: value }
    setColors(newColors)
    setBranding({
      ...branding,
      colors: newColors,
    })
  }

  const handlePreview = () => {
    setShowPreview(!showPreview)
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        🎨 OEM Customization
      </h2>
      
      <div className="space-y-6">
        {/* Company Logo Upload */}
        <div>
          <label className="label">
            Company Logo
          </label>
          <div className="space-y-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/gif,image/svg+xml"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                cursor-pointer"
            />
            <p className="text-xs text-gray-500">
              Accepted formats: JPG, PNG, GIF, SVG (max 5MB)
            </p>

            {logoPreview && (
              <div className="mt-3 p-4 border border-gray-200 rounded-lg bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Preview:</span>
                  <button
                    onClick={handleRemoveLogo}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>
                <img
                  src={logoPreview}
                  alt="Logo preview"
                  className="max-w-xs max-h-32 object-contain mx-auto"
                />
                {logoFile && !branding?.logo_url && (
                  <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="mt-3 w-full btn-primary disabled:opacity-50"
                  >
                    {isUploading ? 'Uploading...' : 'Upload Logo'}
                  </button>
                )}
              </div>
            )}

            {branding?.logo_url && (
              <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  ✓ Logo uploaded successfully
                </p>
              </div>
            )}

            {uploadError && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{uploadError}</p>
              </div>
            )}
          </div>
        </div>

        {/* Brand Colors */}
        <div>
          <label className="label">Brand Colors</label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Primary Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={colors.primary_color}
                  onChange={(e) => handleColorChange('primary_color', e.target.value)}
                  className="h-10 w-20 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={colors.primary_color}
                  onChange={(e) => handleColorChange('primary_color', e.target.value)}
                  className="input-field flex-1"
                  placeholder="#2563eb"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Secondary Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={colors.secondary_color}
                  onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                  className="h-10 w-20 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={colors.secondary_color}
                  onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                  className="input-field flex-1"
                  placeholder="#3b82f6"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Accent Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={colors.accent_color}
                  onChange={(e) => handleColorChange('accent_color', e.target.value)}
                  className="h-10 w-20 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={colors.accent_color}
                  onChange={(e) => handleColorChange('accent_color', e.target.value)}
                  className="input-field flex-1"
                  placeholder="#1e40af"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Company Tagline */}
        <div>
          <label className="label">Company Tagline (Optional)</label>
          <input
            type="text"
            className="input-field"
            value={branding?.tagline || ''}
            onChange={(e) => setBranding({ ...branding, tagline: e.target.value })}
            placeholder="Your company tagline..."
            maxLength={200}
          />
        </div>

        {/* Company Website */}
        <div>
          <label className="label">Company Website (Optional)</label>
          <input
            type="url"
            className="input-field"
            value={branding?.website || ''}
            onChange={(e) => setBranding({ ...branding, website: e.target.value })}
            placeholder="https://yourcompany.com"
          />
        </div>

        {/* Preview Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handlePreview}
            className="btn-secondary w-full"
          >
            {showPreview ? 'Hide Preview' : 'Show Preview'}
          </button>
        </div>

        {/* Branding Preview */}
        {showPreview && (
          <div className="mt-4 p-6 border border-gray-200 rounded-lg bg-gray-50">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">
              Branding Preview
            </h3>
            <div
              style={{
                background: `linear-gradient(135deg, ${colors.primary_color} 0%, ${colors.secondary_color} 100%)`,
                color: 'white',
                padding: '2rem',
                borderRadius: '0.5rem',
                textAlign: 'center',
              }}
            >
              {(logoPreview || branding?.logo_url) && (
                <img
                  src={logoPreview || branding?.logo_url}
                  alt="Company logo"
                  style={{
                    maxWidth: '200px',
                    maxHeight: '100px',
                    margin: '0 auto 1rem',
                    objectFit: 'contain',
                  }}
                />
              )}
              <h1 style={{ margin: 0, fontSize: '2rem' }}>
                {project.company_name || 'Your Company'}
              </h1>
              {branding?.tagline && (
                <p style={{ margin: '0.5rem 0', fontSize: '1.125rem', opacity: 0.9 }}>
                  {branding.tagline}
                </p>
              )}
              <div
                style={{
                  marginTop: '1.5rem',
                  padding: '1rem',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '0.25rem',
                }}
              >
                <p style={{ margin: 0, fontSize: '0.875rem' }}>
                  VMS System Calculator Report
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

