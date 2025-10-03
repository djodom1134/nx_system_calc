/**
 * Main calculator page component with accessibility features
 */

import { useState, useRef, useEffect } from 'react'
import { useCalculatorStore } from '../stores/calculatorStore'
import { apiClient } from '../services/api'
import ProjectForm from '../components/ProjectForm'
import CameraForm from '../components/CameraForm'
import ServerForm from '../components/ServerForm'
import Results from '../components/Results'

export default function Calculator() {
  const {
    project,
    cameraGroups,
    retentionDays,
    serverConfig,
    setResults,
    isCalculating,
    setIsCalculating,
    error,
    setError,
  } = useCalculatorStore()

  const [activeTab, setActiveTab] = useState<'input' | 'results'>('input')
  const errorRef = useRef<HTMLDivElement>(null)
  const resultsAnnouncementRef = useRef<HTMLDivElement>(null)

  // Focus error message when it appears
  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.focus()
    }
  }, [error])

  const handleCalculate = async () => {
    // Validation
    if (!project.project_name || !project.created_by || !project.creator_email) {
      setError('Please fill in all required project fields')
      return
    }

    if (cameraGroups.length === 0) {
      setError('Please add at least one camera group')
      return
    }

    setIsCalculating(true)
    setError(null)

    try {
      const response = await apiClient.calculate({
        project,
        camera_groups: cameraGroups,
        retention_days: retentionDays,
        server_config: serverConfig,
      })

      setResults(response)
      setActiveTab('results')

      // Announce to screen readers
      if (resultsAnnouncementRef.current) {
        resultsAnnouncementRef.current.textContent = 'Calculation complete. Results are now available.'
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed')
    } finally {
      setIsCalculating(false)
    }
  }

  const handleTabChange = (tab: 'input' | 'results') => {
    setActiveTab(tab)
    // Clear error when switching tabs
    if (error) {
      setError(null)
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Screen reader announcements */}
      <div
        ref={resultsAnnouncementRef}
        className="sr-only"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      />

      {/* Tab Navigation */}
      <nav
        className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-200"
        role="tablist"
        aria-label="Calculator sections"
      >
        <button
          role="tab"
          aria-selected={activeTab === 'input'}
          aria-controls="input-panel"
          id="input-tab"
          onClick={() => handleTabChange('input')}
          className={`px-4 sm:px-6 py-3 font-medium transition-colors text-sm sm:text-base ${
            activeTab === 'input'
              ? 'border-b-2'
              : 'text-gray-600 hover:text-gray-800'
          }`}
          style={activeTab === 'input' ? { borderColor: '#407EC9', color: '#407EC9' } : {}}
        >
          Configuration
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'results'}
          aria-controls="results-panel"
          id="results-tab"
          onClick={() => handleTabChange('results')}
          className={`px-4 sm:px-6 py-3 font-medium transition-colors text-sm sm:text-base ${
            activeTab === 'results'
              ? 'border-b-2'
              : 'text-gray-600 hover:text-gray-800'
          }`}
          style={activeTab === 'results' ? { borderColor: '#407EC9', color: '#407EC9' } : {}}
        >
          Results
        </button>
      </nav>

      {/* Error Display */}
      {error && (
        <div
          ref={errorRef}
          role="alert"
          aria-live="assertive"
          tabIndex={-1}
          className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
        >
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-red-500 mr-3 flex-shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <p className="font-bold">Error</p>
              <p>{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Input Tab */}
      <div
        id="input-panel"
        role="tabpanel"
        aria-labelledby="input-tab"
        hidden={activeTab !== 'input'}
        className={activeTab === 'input' ? 'space-y-4 sm:space-y-6' : 'hidden'}
      >
        <ProjectForm />
        <CameraForm />
        <ServerForm />

        <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-4">
          <button
            onClick={handleCalculate}
            disabled={isCalculating}
            className="btn-primary px-6 sm:px-8 py-3 text-base sm:text-lg w-full sm:w-auto"
            aria-busy={isCalculating}
            aria-describedby="calculate-button-help"
          >
            {isCalculating ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>Calculating...</span>
              </span>
            ) : (
              'Calculate System Requirements'
            )}
          </button>
          <span id="calculate-button-help" className="sr-only">
            Click to calculate VMS system requirements based on your configuration
          </span>
        </div>
      </div>

      {/* Results Tab */}
      <div
        id="results-panel"
        role="tabpanel"
        aria-labelledby="results-tab"
        hidden={activeTab !== 'results'}
        className={activeTab === 'results' ? '' : 'hidden'}
      >
        <Results />
      </div>
    </div>
  )
}

