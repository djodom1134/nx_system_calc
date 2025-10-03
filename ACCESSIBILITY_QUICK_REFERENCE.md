# Accessibility Quick Reference Guide

## Quick Accessibility Checklist

### ✅ Keyboard Navigation
- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical and intuitive
- [ ] Focus indicators are clearly visible
- [ ] Skip to main content link is present
- [ ] No keyboard traps exist

### ✅ Screen Readers
- [ ] All images have alt text
- [ ] Form inputs have associated labels
- [ ] ARIA landmarks are used (banner, main, navigation, contentinfo)
- [ ] ARIA labels describe interactive elements
- [ ] Live regions announce dynamic content

### ✅ Visual Design
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] Information is not conveyed by color alone
- [ ] Text can be resized to 200% without loss of functionality
- [ ] Focus indicators are visible

### ✅ Forms
- [ ] All inputs have labels
- [ ] Required fields are marked
- [ ] Error messages are clear and linked to inputs
- [ ] Autocomplete attributes are used where appropriate

### ✅ Responsive Design
- [ ] Works on mobile (320px+)
- [ ] Touch targets are at least 44x44px
- [ ] Text is at least 16px (prevents iOS zoom)
- [ ] Layout adapts to different screen sizes

## Common ARIA Attributes

### Landmarks
```html
<header role="banner">
<nav role="navigation">
<main role="main">
<footer role="contentinfo">
```

### Form Accessibility
```html
<label htmlFor="input-id">Label</label>
<input 
  id="input-id"
  aria-required="true"
  aria-invalid="false"
  aria-describedby="error-id"
/>
<span id="error-id" role="alert">Error message</span>
```

### Live Regions
```html
<div role="alert" aria-live="assertive">Critical error</div>
<div role="status" aria-live="polite">Status update</div>
```

### Tab Navigation
```html
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Tab 2</button>
</div>
<div id="panel-1" role="tabpanel" aria-labelledby="tab-1">Content</div>
```

### Buttons and Links
```html
<button aria-label="Close dialog">×</button>
<button aria-busy="true">Loading...</button>
<button disabled aria-disabled="true">Disabled</button>
```

## Responsive Design Patterns

### Tailwind CSS Breakpoints
```tsx
// Mobile first
<div className="px-4 sm:px-6 lg:px-8">
<h1 className="text-2xl sm:text-3xl lg:text-4xl">
<div className="space-y-4 sm:space-y-6">
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
```

### Touch Targets
```css
/* Minimum 44x44px for touch targets */
button, a, input[type="checkbox"] {
  min-height: 44px;
  min-width: 44px;
}
```

### Prevent iOS Zoom
```css
/* Use 16px minimum font size */
input, select, textarea {
  font-size: 16px;
}
```

## CSS Utilities

### Screen Reader Only
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Focus Visible
```css
*:focus-visible {
  outline: none;
  ring: 2px solid #3b82f6;
  ring-offset: 2px;
}
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### High Contrast
```css
@media (prefers-contrast: high) {
  .btn-primary {
    border: 2px solid white;
  }
}
```

## Testing Tools

### Browser Extensions
- **axe DevTools**: Automated accessibility testing
- **WAVE**: Visual accessibility evaluation
- **Lighthouse**: Performance and accessibility audits

### Screen Readers
- **macOS**: VoiceOver (Cmd+F5)
- **Windows**: NVDA (free) or JAWS
- **iOS**: VoiceOver (Settings > Accessibility)
- **Android**: TalkBack (Settings > Accessibility)

### Manual Testing
1. **Keyboard Only**: Unplug mouse, navigate with Tab/Shift+Tab/Enter/Space
2. **Zoom**: Test at 200% zoom
3. **Color Contrast**: Use browser DevTools or online checkers
4. **Mobile**: Test on real devices or browser DevTools

## Common Issues and Fixes

### Issue: Missing Label
```tsx
// ❌ Bad
<input type="text" placeholder="Name" />

// ✅ Good
<label htmlFor="name">Name</label>
<input id="name" type="text" placeholder="John Doe" />
```

### Issue: Poor Focus Indicator
```css
/* ❌ Bad */
button:focus {
  outline: none;
}

/* ✅ Good */
button:focus-visible {
  outline: none;
  ring: 2px solid #3b82f6;
  ring-offset: 2px;
}
```

### Issue: Color Only Information
```tsx
// ❌ Bad
<span style={{ color: 'red' }}>*</span>

// ✅ Good
<span className="text-red-500" aria-label="required">*</span>
```

### Issue: Inaccessible Error
```tsx
// ❌ Bad
<div className="error">Error occurred</div>

// ✅ Good
<div role="alert" aria-live="assertive" className="error">
  Error occurred
</div>
```

### Issue: Small Touch Targets
```css
/* ❌ Bad */
button {
  padding: 4px 8px;
}

/* ✅ Good */
button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
}
```

## WCAG 2.1 Level AA Quick Reference

### Perceivable
- **1.1.1**: Non-text content has text alternatives
- **1.3.1**: Info and relationships can be programmatically determined
- **1.4.3**: Color contrast is at least 4.5:1
- **1.4.11**: UI components have 3:1 contrast

### Operable
- **2.1.1**: All functionality available via keyboard
- **2.4.3**: Focus order is logical
- **2.4.7**: Focus indicator is visible
- **2.5.5**: Touch targets are at least 44x44px (Level AAA)

### Understandable
- **3.2.3**: Navigation is consistent
- **3.3.1**: Errors are identified
- **3.3.2**: Labels or instructions are provided
- **3.3.3**: Error suggestions are provided

### Robust
- **4.1.2**: Name, role, value are available to assistive tech
- **4.1.3**: Status messages can be programmatically determined

## Resources

- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **WebAIM**: https://webaim.org/
- **A11y Project**: https://www.a11yproject.com/
- **MDN**: https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **Inclusive Components**: https://inclusive-components.design/

## Quick Commands

```bash
# Run accessibility tests
bash scripts/test_accessibility.sh

# Start dev server
cd frontend && npm run dev

# Run Lighthouse audit
# Open DevTools > Lighthouse > Accessibility

# Enable VoiceOver (macOS)
# Cmd+F5

# Enable NVDA (Windows)
# Download from nvaccess.org
```

---

**Remember**: Accessibility is not a feature, it's a requirement. Build it in from the start!

