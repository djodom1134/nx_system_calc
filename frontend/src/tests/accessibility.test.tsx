/**
 * Accessibility tests for the Nx System Calculator
 * 
 * These tests verify WCAG 2.1 Level AA compliance
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import userEvent from '@testing-library/user-event'
import App from '../App'
import Calculator from '../pages/Calculator'
import ProjectForm from '../components/ProjectForm'
import CameraForm from '../components/CameraForm'
import ServerForm from '../components/ServerForm'

// Extend Jest matchers
expect.extend(toHaveNoViolations)

describe('Accessibility Tests', () => {
  describe('App Component', () => {
    it('should not have any accessibility violations', async () => {
      const { container } = render(<App />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('should have skip to main content link', () => {
      render(<App />)
      const skipLink = screen.getByText(/skip to main content/i)
      expect(skipLink).toBeInTheDocument()
      expect(skipLink).toHaveAttribute('href', '#main-content')
    })

    it('should have proper landmark roles', () => {
      render(<App />)
      expect(screen.getByRole('banner')).toBeInTheDocument() // header
      expect(screen.getByRole('main')).toBeInTheDocument() // main
      expect(screen.getByRole('contentinfo')).toBeInTheDocument() // footer
    })

    it('should have proper heading hierarchy', () => {
      render(<App />)
      const headings = screen.getAllByRole('heading')
      expect(headings[0]).toHaveAttribute('aria-level', '1') // h1
    })
  })

  describe('Keyboard Navigation', () => {
    it('should allow keyboard navigation through all interactive elements', async () => {
      const user = userEvent.setup()
      render(<App />)

      // Tab through elements
      await user.tab()
      expect(screen.getByText(/skip to main content/i)).toHaveFocus()

      await user.tab()
      // Should focus on first interactive element in main content
    })

    it('should show focus indicators on all focusable elements', async () => {
      const user = userEvent.setup()
      render(<Calculator />)

      const buttons = screen.getAllByRole('button')
      for (const button of buttons) {
        button.focus()
        expect(button).toHaveFocus()
      }
    })

    it('should support Enter and Space keys for buttons', async () => {
      const user = userEvent.setup()
      render(<Calculator />)

      const configTab = screen.getByRole('tab', { name: /configuration/i })
      
      // Test Enter key
      configTab.focus()
      await user.keyboard('{Enter}')
      expect(configTab).toHaveAttribute('aria-selected', 'true')

      // Test Space key
      const resultsTab = screen.getByRole('tab', { name: /results/i })
      resultsTab.focus()
      await user.keyboard(' ')
      expect(resultsTab).toHaveAttribute('aria-selected', 'true')
    })
  })

  describe('Screen Reader Support', () => {
    it('should have ARIA labels for all form inputs', () => {
      render(<ProjectForm />)

      const projectNameInput = screen.getByLabelText(/project name/i)
      expect(projectNameInput).toHaveAttribute('aria-required', 'true')

      const createdByInput = screen.getByLabelText(/created by/i)
      expect(createdByInput).toHaveAttribute('aria-required', 'true')

      const emailInput = screen.getByLabelText(/^email/i)
      expect(emailInput).toHaveAttribute('aria-required', 'true')
    })

    it('should announce errors to screen readers', async () => {
      render(<Calculator />)

      const calculateButton = screen.getByRole('button', { name: /calculate/i })
      await userEvent.click(calculateButton)

      const errorAlert = await screen.findByRole('alert')
      expect(errorAlert).toBeInTheDocument()
      expect(errorAlert).toHaveAttribute('aria-live', 'assertive')
    })

    it('should have live regions for dynamic content', () => {
      render(<Calculator />)

      const liveRegion = screen.getByRole('status')
      expect(liveRegion).toHaveAttribute('aria-live', 'polite')
    })

    it('should have proper tab panel structure', () => {
      render(<Calculator />)

      const tablist = screen.getByRole('tablist')
      expect(tablist).toHaveAttribute('aria-label', 'Calculator sections')

      const tabs = screen.getAllByRole('tab')
      expect(tabs).toHaveLength(2)

      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('aria-selected')
        expect(tab).toHaveAttribute('aria-controls')
      })
    })
  })

  describe('Form Accessibility', () => {
    it('should associate labels with inputs', () => {
      render(<ProjectForm />)

      const inputs = screen.getAllByRole('textbox')
      inputs.forEach(input => {
        expect(input).toHaveAccessibleName()
      })
    })

    it('should mark required fields appropriately', () => {
      render(<ProjectForm />)

      const projectNameInput = screen.getByLabelText(/project name/i)
      expect(projectNameInput).toHaveAttribute('required')
      expect(projectNameInput).toHaveAttribute('aria-required', 'true')
    })

    it('should provide error messages for invalid inputs', async () => {
      render(<ProjectForm />)

      const projectNameInput = screen.getByLabelText(/project name/i)
      expect(projectNameInput).toHaveAttribute('aria-invalid')
      
      if (projectNameInput.getAttribute('aria-invalid') === 'true') {
        const errorId = projectNameInput.getAttribute('aria-describedby')
        expect(errorId).toBeTruthy()
      }
    })

    it('should have autocomplete attributes for common fields', () => {
      render(<ProjectForm />)

      const emailInput = screen.getByLabelText(/^email/i)
      expect(emailInput).toHaveAttribute('autocomplete', 'email')

      const companyInput = screen.getByLabelText(/company name/i)
      expect(companyInput).toHaveAttribute('autocomplete', 'organization')
    })
  })

  describe('Color and Contrast', () => {
    it('should not rely on color alone for information', () => {
      render(<Calculator />)

      // Required fields should have both color and text indicator
      const requiredIndicators = screen.getAllByText('*')
      requiredIndicators.forEach(indicator => {
        expect(indicator).toHaveAttribute('aria-label', 'required')
      })
    })

    it('should have sufficient color contrast', async () => {
      const { container } = render(<App />)
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      })
      expect(results).toHaveNoViolations()
    })
  })

  describe('Responsive Design', () => {
    it('should have viewport meta tag', () => {
      const viewportMeta = document.querySelector('meta[name="viewport"]')
      expect(viewportMeta).toBeInTheDocument()
      expect(viewportMeta).toHaveAttribute('content', expect.stringContaining('width=device-width'))
    })

    it('should have minimum touch target sizes', () => {
      render(<Calculator />)

      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        const styles = window.getComputedStyle(button)
        const minHeight = parseInt(styles.minHeight)
        const minWidth = parseInt(styles.minWidth)
        
        // WCAG 2.1 Level AAA requires 44x44px minimum
        expect(minHeight).toBeGreaterThanOrEqual(44)
        expect(minWidth).toBeGreaterThanOrEqual(44)
      })
    })

    it('should prevent zoom on input focus (iOS)', () => {
      render(<ProjectForm />)

      const inputs = screen.getAllByRole('textbox')
      inputs.forEach(input => {
        const styles = window.getComputedStyle(input)
        const fontSize = parseInt(styles.fontSize)
        
        // Font size should be at least 16px to prevent iOS zoom
        expect(fontSize).toBeGreaterThanOrEqual(16)
      })
    })
  })

  describe('Focus Management', () => {
    it('should focus on error messages when they appear', async () => {
      render(<Calculator />)

      const calculateButton = screen.getByRole('button', { name: /calculate/i })
      await userEvent.click(calculateButton)

      const errorAlert = await screen.findByRole('alert')
      expect(errorAlert).toHaveFocus()
    })

    it('should maintain focus within modal dialogs', () => {
      // Test focus trap in modals if implemented
      // This is a placeholder for future modal implementations
    })

    it('should restore focus after closing dialogs', () => {
      // Test focus restoration
      // This is a placeholder for future modal implementations
    })
  })

  describe('Semantic HTML', () => {
    it('should use semantic HTML elements', () => {
      render(<App />)

      expect(screen.getByRole('banner')).toBeInTheDocument() // <header>
      expect(screen.getByRole('main')).toBeInTheDocument() // <main>
      expect(screen.getByRole('contentinfo')).toBeInTheDocument() // <footer>
      expect(screen.getByRole('navigation')).toBeInTheDocument() // <nav>
    })

    it('should use buttons for actions and links for navigation', () => {
      render(<Calculator />)

      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button.tagName).toBe('BUTTON')
      })
    })
  })

  describe('Loading States', () => {
    it('should announce loading states to screen readers', async () => {
      render(<Calculator />)

      const calculateButton = screen.getByRole('button', { name: /calculate/i })
      
      // When calculating, button should have aria-busy
      // This would need to be tested with actual API call
    })

    it('should have accessible loading spinner', () => {
      render(<Calculator />)

      // Loading spinner should have aria-hidden or proper label
      const spinners = document.querySelectorAll('.spinner')
      spinners.forEach(spinner => {
        expect(spinner).toHaveAttribute('aria-hidden', 'true')
      })
    })
  })

  describe('Error Handling', () => {
    it('should provide clear error messages', async () => {
      render(<Calculator />)

      const calculateButton = screen.getByRole('button', { name: /calculate/i })
      await userEvent.click(calculateButton)

      const errorMessage = await screen.findByRole('alert')
      expect(errorMessage).toHaveTextContent(/please fill in all required/i)
    })

    it('should link error messages to form fields', () => {
      render(<ProjectForm />)

      const projectNameInput = screen.getByLabelText(/project name/i)
      const describedBy = projectNameInput.getAttribute('aria-describedby')
      
      if (describedBy) {
        const errorMessage = document.getElementById(describedBy)
        expect(errorMessage).toBeInTheDocument()
      }
    })
  })
})

