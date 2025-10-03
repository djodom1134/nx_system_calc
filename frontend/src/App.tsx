import { useState, useEffect } from 'react'
import Calculator from './pages/Calculator'
import './App.css'

function App() {
  const [showSkipLink, setShowSkipLink] = useState(false)

  // Announce page changes to screen readers
  useEffect(() => {
    document.title = 'Nx System Calculator - VMS Hardware Requirements'
  }, [])

  const handleSkipToMain = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()
    const mainContent = document.getElementById('main-content')
    if (mainContent) {
      mainContent.focus()
      mainContent.scrollIntoView()
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F5F5F5' }}>
      {/* Skip to main content link for keyboard users */}
      <a
        href="#main-content"
        onClick={handleSkipToMain}
        onFocus={() => setShowSkipLink(true)}
        onBlur={() => setShowSkipLink(false)}
        className={`skip-link ${showSkipLink ? 'skip-link-visible' : ''}`}
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>

      <header
        role="banner"
        className="shadow-lg relative overflow-hidden"
        style={{
          backgroundColor: '#1D252D',
          backgroundImage: 'url(/tile.png)',
          backgroundRepeat: 'repeat',
          backgroundPosition: 'center',
          backgroundSize: 'auto'
        }}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 relative z-10">
          <div className="flex items-center gap-4 sm:gap-6">
            <img
              src="/logo.webp"
              alt="Network Optix Logo"
              className="h-6 sm:h-7 lg:h-8 w-auto flex-shrink-0 relative z-10"
            />
            <div className="flex-1 text-center">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white">
                Nx System Calculator
              </h1>
              <p className="text-gray-300 mt-1 text-sm sm:text-base lg:text-lg">
                VMS Hardware & Storage Requirements Calculator
              </p>
            </div>
          </div>
        </div>
      </header>

      <main
        id="main-content"
        role="main"
        className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8"
        tabIndex={-1}
        aria-label="Calculator application"
      >
        <Calculator />
      </main>

      <footer role="contentinfo" style={{ backgroundColor: '#1D252D' }} className="text-gray-300 mt-12 sm:mt-16 border-t border-gray-700">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
          <p className="text-sm sm:text-base">
            &copy; 2025 Network Optix, Inc. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App

