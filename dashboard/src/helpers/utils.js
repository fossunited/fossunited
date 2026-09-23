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
 * Turn a raw frappe-ui error into a { kind, message } pair a page can act on.
 *
 * Handles the vendored frappe-ui bug where a non-JSON 429 response body
 * (e.g. from Frappe's site-wide rate limiter, as opposed to our own
 * @rate_limit-decorated methods) crashes its own error parser on
 * `error.exc` before it can build a proper Error — the `err` a caller
 * receives in that case is a bare TypeError with no `.messages`/`.response`,
 * which is where "Cannot read properties of undefined (reading 'exc')"
 * toasts come from. We fall back to a clean generic message instead.
 *
 * @param {Error} error - Error from frappe-ui/api
 * @returns {{ kind: 'rate-limit'|'auth'|'permission'|'not-found'|'validation'|'unknown', message: string }}
 */
export function getFriendlyError(error) {
  if (typeof error === 'string') {
    return { kind: 'validation', message: error }
  }

  const status = error?.response?.status ?? error?.status
  const excType = error?.exc_type
  const serverMessage =
    Array.isArray(error?.messages) && error.messages.length ? error.messages[0] : null

  if (excType === 'RateLimitExceededError' || status === 429) {
    // Frappe's own rate-limit message doesn't say how long, so we always
    // show our own text here rather than the server's generic one.
    return {
      kind: 'rate-limit',
      message:
        "You've made too many attempts. Please try again after 12 hours from your last " +
        'attempt, or email developers@fossunited.org if you need this done sooner.',
    }
  }
  if (excType === 'AuthenticationError' || status === 401) {
    return {
      kind: 'auth',
      message: serverMessage || 'Please log in to continue.',
    }
  }
  if (excType === 'PermissionError' || status === 403) {
    return {
      kind: 'permission',
      message: serverMessage || 'You are not authorized to perform this action.',
    }
  }
  if (excType === 'DoesNotExistError' || status === 404) {
    return {
      kind: 'not-found',
      message: serverMessage || "We couldn't find what you're looking for.",
    }
  }
  if (serverMessage) {
    return { kind: 'validation', message: serverMessage }
  }
  return {
    kind: 'unknown',
    message: 'Something went wrong. Please try again in a bit.',
  }
}

/**
 * Minimal error handler - shows error message with console hint
 * @param {Error} error - Error from frappe-ui/api
 * @param {string} fallback - Fallback message (optional)
 */
export function showError(error, fallback = 'An error occurred') {
  const { message } = getFriendlyError(error)
  const displayMessage = `${fallback}: ${message}`

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
