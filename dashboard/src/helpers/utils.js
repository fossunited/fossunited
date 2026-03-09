import { computed } from 'vue'
import { toast } from 'vue-sonner'
import DOMPurify from 'dompurify'

export const truncateStr = (title, len) => {
  return title.length > len ? title.substring(0, len) + '...' : title
}

export const redirectRoute = (route) => {
  window.open(document.location.origin + '/' + route, '_blank')
}

export const createAbsoluteUrlFromRoute = (route) => {
  return window.location.origin + '/' + route
}

export const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
}

// Remove any empty <p> tag, and add custom margins
export const cleanedHTML = (htmlData) => {
  const html = htmlData || ''
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = DOMPurify.sanitize(html)

  // Process each <p> tag
  tempDiv.querySelectorAll('p').forEach((p) => {
    const text = p.textContent.replace(/\u00a0/g, ' ').trim()
    if (text === '') {
      p.remove()
    } else {
      p.classList.add('my-2')
    }
  })
  return tempDiv.innerHTML
}

export const isValidUrl = (link) => {
  try {
    const url = new URL(link)
    return url.protocol === 'https:'
  } catch {
    return false
  }
}

export const isSmallScreen = computed(() => window.innerWidth < 768)

/**
 * Minimal error handler - shows error message with console hint
 * @param {Error} error - Error from frappe-ui/api
 * @param {string} fallback - Fallback message (optional)
 */
export function showError(error, fallback = 'An error occurred') {
  const isRateLimited = error?.response?.status === 429 || error?.status === 429
  const apiMessage = typeof error === 'string' ? error : error?.messages?.[0] || error?.message
  const message = isRateLimited
    ? 'Too many requests/attempts. Take rest & Please try again after an hour.'
    : apiMessage || fallback
  const displayMessage = message === fallback ? fallback : `${fallback}: ${message}`

  console.error('API Error:', error)

  toast.error(displayMessage, {
    duration: 5000,
    action: {
      label: 'Details',
      onClick: () => {
        console.group('🔍 Error Details')
        console.error(error)
        console.groupEnd()
        toast.info('Check console (Press F12)')
      },
    },
  })
}
