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

export const redirectToExternalUrl = (url) => {
  window.open(url, '_blank')
}

export const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
}

export const triggerDownload = (url, filename) => {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

/**
 * Fetch a URL and return an object URL for its blob
 */
export async function fetchBlobUrl(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  const blob = await res.blob()
  return URL.createObjectURL(blob)
}

/**
 * Fetch a file and trigger its download, resolving once the download has
 * started; unlike a plain <a download> click, this gives callers a promise
 * to await, so a "loading" state can be shown until the file is ready.
 */
export async function fetchAndDownload(url, filename) {
  const blobUrl = await fetchBlobUrl(url)
  triggerDownload(blobUrl, filename)
  URL.revokeObjectURL(blobUrl)
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

// True when a TipTap/rich-text HTML string has real content, false for
// blank docs like '<p></p>', '<p>&nbsp;</p>', or whitespace-only strings.
export const hasHtmlContent = (htmlData) => {
  return cleanedHTML(htmlData).trim() !== ''
}

export const ensureHttpsPrefix = (url) => {
  if (!url || url.startsWith('http://') || url.startsWith('https://')) return url
  return 'https://' + url
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
