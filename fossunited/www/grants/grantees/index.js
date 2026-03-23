let originalItems = []

document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll('.grant-item')

  originalItems = Array.from(items)

  const searchInput = document.getElementById('search')
  const groupBySelect = document.getElementById('group-by')
  const sortSelect = document.getElementById('sort')

  let searchTimeout
  searchInput?.addEventListener('input', () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(applyFilters, 300)
  })

  groupBySelect?.addEventListener('change', applyFilters)
  sortSelect?.addEventListener('change', applyFilters)

  const params = new URLSearchParams(window.location.search)
  const searchFromURL = params.get('s') || params.get('search')

  if (searchFromURL && searchInput) {
    searchInput.value = searchFromURL
  }

  applyFilters()
})


function applyFilters() {
  const searchInput = document.getElementById('search')
  const groupBySelect = document.getElementById('group-by')
  const sortSelect = document.getElementById('sort')

  const searchTerm = searchInput?.value.toLowerCase().trim() || ''
  const groupBy = groupBySelect?.value
  const sortBy = sortSelect?.value

  const resultsContainer = document.getElementById('results-count-container')
  if (resultsContainer) {
    resultsContainer.style.display = searchTerm ? '' : 'none'
  }

  const allItems = originalItems.map((item) => item.cloneNode(true))

  const visibleItems = allItems.filter((item) => {
    if (!searchTerm) return true

    return (
      item.dataset.name?.includes(searchTerm) ||
      item.dataset.description?.includes(searchTerm) ||
      item.dataset.sponsor?.includes(searchTerm) ||
      item.dataset.url?.includes(searchTerm)
    )
  })

  const resultsCount = document.getElementById('results-count')
  if (searchTerm && resultsCount) {
    resultsCount.textContent =
      `Showing ${visibleItems.length} grant${visibleItems.length !== 1 ? 's' : ''}`
  }

  visibleItems.sort((a, b) => {
    switch (sortBy) {
      case 'date-asc':
        return new Date(a.dataset.date) - new Date(b.dataset.date)
      case 'date-desc':
        return new Date(b.dataset.date) - new Date(a.dataset.date)
      case 'name-asc':
        return a.dataset.name.localeCompare(b.dataset.name)
      case 'name-desc':
        return b.dataset.name.localeCompare(a.dataset.name)
      default:
        return 0
    }
  })

  const container = document.getElementById('grants-container')
  if (!container) return

  container.innerHTML = ''

  if (groupBy === 'year') {
    const yearGroups = {}

    visibleItems.forEach((item) => {
      const year = item.dataset.year
      if (!yearGroups[year]) yearGroups[year] = []
      yearGroups[year].push(item)
    })

    Object.keys(yearGroups)
      .sort((a, b) => b - a)
      .forEach((year) => {
        addYearSection(year, yearGroups[year])
      })

  } else if (groupBy === 'type') {
    groupByField(visibleItems, 'type', {
      Project: { title: 'Project Grants', icon: 'ti ti-device-imac-code' },
      Event: { title: 'Event Grants', icon: 'ti ti-building-circus' },
      Fellowship: { title: 'Fellowship Grants', icon: 'ti ti-heart-handshake' },
    })

  } else if (groupBy === 'amount') {
    const amountGroups = {}

    visibleItems.forEach((item) => {
      const range = getAmountRange(item.dataset.amount)
      if (!amountGroups[range]) amountGroups[range] = []
      amountGroups[range].push(item)
    })

    ;[
      'Above ₹5,00,000',
      '₹2,00,000 - ₹5,00,000',
      '₹1,00,000 - ₹2,00,000',
      '₹50,000 - ₹1,00,000',
      'Under ₹50,000',
      'Not Specified',
    ].forEach((range) => {
      if (amountGroups[range]?.length > 0) {
        addSection(range, 'ti ti-currency-rupee', amountGroups[range])
      }
    })

  } else {
    const flatContainer = document.createElement('div')
    flatContainer.className = 'd-flex flex-column'

    visibleItems.forEach((item) => {
      item.classList.add('mb-3')
      flatContainer.appendChild(item)
    })
    container.appendChild(flatContainer)
  }

  const noResults = document.getElementById('no-results')

  if (noResults) {
    noResults.style.display = visibleItems.length === 0 ? '' : 'none'
  }

  container.style.display = visibleItems.length === 0 ? 'none' : ''
}

function addYearSection(year, items) {
  const section = document.createElement('div')
  section.className = 'mb-4'

  const sectionId = `year-content-${year}`

  section.innerHTML = `
    <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2"
      role="button"
      tabindex="0"
      aria-expanded="true"
      aria-controls="${sectionId}"
      onclick="toggleSection('${sectionId}')"
      onkeydown="if (event.key === 'Enter' || event.key === ' ') toggleSection('${sectionId}')"
      style="cursor:pointer;">
      <div>
        <strong>${year}</strong>
        <span class="text-muted small">(${items.length})</span>
      </div>
      <i class="ti ti-chevron-down v3-toggle-icon"></i>
    </div>
    <div class="d-flex flex-column" id="${sectionId}"></div>
  `

  const content = section.querySelector(`#${sectionId}`)
  items.forEach((item) => {
    item.classList.add('mb-3')
    content.appendChild(item)
  })

  document.getElementById('grants-container').appendChild(section)
}

function groupByField(items, field, configs) {
  const groups = {}

  items.forEach((item) => {
    const key = item.dataset[field]
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
  })

  Object.keys(configs).forEach((key) => {
    if (groups[key]?.length > 0) {
      addSection(configs[key].title, configs[key].icon, groups[key])
    }
  })
}


function addSection(title, icon, items) {
  const section = document.createElement('div')
  section.className = 'mb-5'

  section.innerHTML = `
    <div class="border-bottom pb-2 mb-3">
      <div class="d-flex align-items-center">
        <i class="${icon}"></i>
        <strong>${title}</strong>
        <span class="text-muted small">(${items.length})</span>
      </div>
    </div>
    <div class="d-flex flex-column grants-section-content"></div>
  `

  const content = section.querySelector('.grants-section-content')
  items.forEach((item) => {
    item.classList.add('mb-3')
    content.appendChild(item)
  })

  document.getElementById('grants-container').appendChild(section)
}

function getAmountRange(amount) {
  if (!amount || amount === 'N/A') return 'Not Specified'

  const num = parseFloat(String(amount).replace(/[^\d.]/g, '')) || 0

  if (num === 0) return 'Not Specified'
  if (num < 50000) return 'Under ₹50,000'
  if (num < 100000) return '₹50,000 - ₹1,00,000'
  if (num < 200000) return '₹1,00,000 - ₹2,00,000'
  if (num < 500000) return '₹2,00,000 - ₹5,00,000'

  return 'Above ₹5,00,000'
}