import { computed } from 'vue'

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
  tempDiv.innerHTML = html

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
