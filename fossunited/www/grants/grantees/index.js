let originalItems = []

document.addEventListener('DOMContentLoaded', () => {
  // Store original items once
  originalItems = Array.from(document.querySelectorAll('.grant-item')).map((item) =>
    item.cloneNode(true),
  )

  const searchInput = document.getElementById('search')
  const groupBySelect = document.getElementById('group-by')
  const sortSelect = document.getElementById('sort')

  let searchTimeout
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(applyFilters, 300)
  })

  groupBySelect.addEventListener('change', applyFilters)
  sortSelect.addEventListener('change', applyFilters)

  applyFilters()
})

function toggleYear(id) {
  const content = document.getElementById(id)
  const header = content?.previousElementSibling
  content.classList.toggle('hidden')
  header?.querySelector('.v3-toggle-icon')?.classList.toggle('rotated')
  header?.setAttribute('aria-expanded', !content.classList.contains('hidden'))
}

function applyFilters() {
  const searchTerm = document.getElementById('search').value.toLowerCase().trim()
  const groupBy = document.getElementById('group-by').value
  const sortBy = document.getElementById('sort').value

  // Show/hide results count
  document.getElementById('results-count-container').style.display = searchTerm ? '' : 'none'

  // Use stored original items
  const allItems = originalItems.map((item) => item.cloneNode(true))

  // Filter items
  const visibleItems = allItems.filter((item) => {
    if (!searchTerm) return true
    return (
      item.dataset.name.includes(searchTerm) ||
      item.dataset.description.includes(searchTerm) ||
      item.dataset.sponsor.includes(searchTerm) ||
      item.dataset.url.includes(searchTerm)
    )
  })

  // Update results count
  if (searchTerm) {
    document.getElementById('results-count').textContent =
      `Showing ${visibleItems.length} grant${visibleItems.length !== 1 ? 's' : ''}`
  }

  // Sort visible items
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

  // Rebuild container based on grouping
  const container = document.getElementById('grants-container')
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
  } else if (groupBy === 'flat') {
    const flatContainer = document.createElement('div')
    flatContainer.className = 'd-flex flex-column v3-grant-year-content'
    visibleItems.forEach((item) => flatContainer.appendChild(item))
    container.appendChild(flatContainer)
  }

  // Show/hide no results
  const noResults = document.getElementById('no-results')
  noResults.style.display = visibleItems.length === 0 ? '' : 'none'
  container.style.display = visibleItems.length === 0 ? 'none' : ''
}

function addYearSection(year, items) {
  const section = document.createElement('div')
  section.className = 'v3-grant-year-section'
  section.dataset.year = year

  const sectionId = `year-content-${year}`
  section.innerHTML = `
       <div class="v3-section-header d-flex justify-content-between align-items-center"
       role="button"
       tabindex="0"
       onclick="toggleYear('${sectionId}')"
       onkeydown="if (event.key === 'Enter' || event.key === ' ') toggleYear('${sectionId}')"
       style="cursor:pointer;">
       <div class="v3-section-title">
       <span>${year}</span>
       <span class="v3-text-tertiary" style="font-size:0.875rem;">(${items.length})</span>
       </div>
       <hr />
       <i class="ti ti-chevron-down v3-toggle-icon" aria-hidden="true"></i>
       </div>
       <div class="v3-grant-year-content d-flex flex-column" id="${sectionId}"></div>
      `

  const content = section.querySelector('.v3-grant-year-content')
  items.forEach((item) => content.appendChild(item))
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
       <div class="v3-section-header">
       <div class="v3-section-title">
       <i class="${icon} v3-grant-icon-sm"></i>
       <span>${title}</span>
       <span class="v3-text-tertiary" style="font-size:0.875rem;margin-left:0.5rem;">(${items.length})</span>
       </div>
       <hr />
       </div>
       <div class="d-flex flex-column v3-grant-year-content"></div>
      `
  const content = section.querySelector('.v3-grant-year-content')
  items.forEach((item) => content.appendChild(item))
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
