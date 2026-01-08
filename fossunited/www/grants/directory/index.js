document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search')
  const sortSelect = document.getElementById('sort')
  const listEl = document.getElementById('grants-list')
  const emptyEl = document.getElementById('empty')
  const countEl = document.getElementById('project-count')

  const tagsPanel = document.getElementById('tags-panel')
  const toggleTagsBtn = document.getElementById('toggle-tags')

  const paginationEl = document.getElementById('pagination')
  const prevBtn = document.getElementById('prev-btn')
  const nextBtn = document.getElementById('next-btn')
  const pageNumbers = document.getElementById('page-numbers')

  const ITEMS_PER_PAGE = 25
  const TAG_BATCH_SIZE = 30

  const state = {
    query: '',
    sort: 'created-desc',
    page: 1,
    tags: new Set(),
    tagsExpanded: false,
  }

  const rawData = JSON.parse(document.getElementById('grants-data').textContent)

  function normalizeData(raw) {
    const allTags = new Set()

    const grants = raw.map((d) => {
      const tags = [...new Set(d.projects.flatMap((p) => p.tags || []))]

      tags.forEach((t) => allTags.add(t))

      const created = new Date(d.created)
      const modified = new Date(d.modified)

      return {
        name: d.entity?.name || d.name,
        route: d.route,
        description: truncateStr(d.entity?.description || '', 150),
        tags,
        projectsCount: d.projects.length,
        created,
        modified,
        createdFmt: formatShortDate(created),
        modifiedFmt: formatShortDate(modified),
      }
    })

    return {
      grants,
      allTags: [...allTags].sort(),
    }
  }

  const data = normalizeData(rawData)

  const sorters = {
    'created-desc': (a, b) => b.created - a.created,
    'modified-desc': (a, b) => b.modified - a.modified,
    'name-asc': (a, b) => a.name.localeCompare(b.name),
    'name-desc': (a, b) => b.name.localeCompare(a.name),
  }

  function applyFilters(grants) {
    const q = state.query.toLowerCase()

    return grants
      .filter((g) => {
        const matchesQuery =
          !q || g.name.toLowerCase().includes(q) || g.tags.some((t) => t.toLowerCase().includes(q))

        const matchesTags =
          state.tags.size === 0 ||
          [...state.tags].every((tag) => g.tags.map((t) => t.toLowerCase()).includes(tag))

        return matchesQuery && matchesTags
      })
      .sort(sorters[state.sort])
  }

  function paginate(items) {
    const start = (state.page - 1) * ITEMS_PER_PAGE
    return items.slice(start, start + ITEMS_PER_PAGE)
  }

  function renderGrantTags(tags) {
    if (!tags.length) return ''

    return `
      <div class="v3-grant-tags">
        ${tags
          .map((t) => {
            const active = state.tags.has(t.toLowerCase()) ? 'active' : ''
            return `
            <span
              class="v3-grant-tag ${active}"
              data-tag="${t.toLowerCase()}"
            >${t}</span>
          `
          })
          .join('')}
      </div>
    `
  }

  function grantCard(g) {
    const showUpdated = state.sort === 'modified-desc' && g.modifiedFmt !== g.createdFmt

    return `
      <a href="/${g.route}" class="v3-card v3-clickable d-flex flex-column gap-1">
        <div class="d-flex justify-content-between align-items-start flex-wrap">
          <h3 class="v3-text-primary mb-0 d-flex align-items-center flex-wrap gap-1" style="font-size:1.1rem;">
            ${g.name}
            <span class="v3-grant-tag">${g.projectsCount} Projects</span>
          </h3>
          <div class="v3-text-tertiary" style="font-size:0.8rem;">
            ${
              showUpdated
                ? `<i class="ti ti-refresh"></i> ${g.modifiedFmt}`
                : `<i class="ti ti-calendar-plus"></i> ${g.createdFmt}`
            }
          </div>
        </div>
        ${g.description ? `<p class="v3-text-secondary mb-0">${g.description}</p>` : ''}
        ${renderGrantTags(g.tags)}
      </a>
    `
  }

  function renderList(items) {
    listEl.innerHTML = items.map(grantCard).join('')
  }

  function renderTagsPanel() {
    tagsPanel.innerHTML = ''

    const visibleTags = state.tagsExpanded ? data.allTags : data.allTags.slice(0, TAG_BATCH_SIZE)

    visibleTags.forEach((tag) => {
      const el = document.createElement('span')
      el.className = `v3-grant-tag ${state.tags.has(tag.toLowerCase()) ? 'active' : ''}`
      el.textContent = tag
      el.dataset.tag = tag.toLowerCase()
      el.onclick = () => toggleTag(tag.toLowerCase())
      tagsPanel.appendChild(el)
    })

    if (!state.tagsExpanded && data.allTags.length > TAG_BATCH_SIZE) {
      const more = document.createElement('span')
      more.className = 'v3-grant-tag'
      more.textContent = `+ ${data.allTags.length - TAG_BATCH_SIZE} more`
      more.onclick = () => {
        state.tagsExpanded = true
        render()
      }
      tagsPanel.appendChild(more)
    }
  }

  function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE)

    if (totalPages <= 1) {
      paginationEl.style.display = 'none'
      return
    }

    paginationEl.style.display = 'flex'
    prevBtn.disabled = state.page === 1
    nextBtn.disabled = state.page === totalPages

    pageNumbers.innerHTML = ''

    for (let i = 1; i <= totalPages; i++) {
      if (Math.abs(i - state.page) > 2 && i !== 1 && i !== totalPages) continue

      const btn = document.createElement('button')
      btn.className = 'v3-btn v3-btn-secondary'
      btn.textContent = i
      if (i === state.page) btn.classList.add('active')

      btn.onclick = () => {
        state.page = i
        updateURL()
        render()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }

      pageNumbers.appendChild(btn)
    }
  }

  function initFromURL() {
    const params = new URLSearchParams(window.location.search)

    if (params.get('tags')) {
      params
        .get('tags')
        .split(',')
        .forEach((t) => state.tags.add(t))
      tagsPanel.style.display = 'flex'
    }

    if (params.get('sort')) {
      state.sort = params.get('sort')
      sortSelect.value = state.sort
    }

    if (params.get('page')) {
      state.page = parseInt(params.get('page'), 10) || 1
    }
  }

  function updateURL() {
    const params = new URLSearchParams()

    if (state.tags.size) params.set('tags', [...state.tags].join(','))
    if (state.sort !== 'created-desc') params.set('sort', state.sort)
    if (state.page > 1) params.set('page', state.page)

    const url = params.toString() ? `${location.pathname}?${params.toString()}` : location.pathname

    history.replaceState({}, '', url)
  }

  function toggleTag(tag) {
    state.tags.has(tag) ? state.tags.delete(tag) : state.tags.add(tag)

    state.page = 1
    tagsPanel.style.display = 'flex'
    render()
  }

  function render() {
    const filtered = applyFilters(data.grants)
    const pageItems = paginate(filtered)

    renderList(pageItems)
    renderTagsPanel()
    renderPagination(filtered.length)

    emptyEl.style.display = filtered.length ? 'none' : 'block'
    countEl.textContent = filtered.length

    updateURL()
  }

  searchInput.addEventListener('input', (e) => {
    state.query = e.target.value
    state.page = 1
    render()
  })

  sortSelect.addEventListener('change', (e) => {
    state.sort = e.target.value
    state.page = 1
    render()
  })

  toggleTagsBtn.onclick = () => {
    tagsPanel.style.display = tagsPanel.style.display === 'none' ? 'flex' : 'none'
  }

  prevBtn.onclick = () => {
    if (state.page > 1) {
      state.page--
      render()
    }
  }

  nextBtn.onclick = () => {
    state.page++
    render()
  }

  listEl.addEventListener('click', (e) => {
    const tag = e.target.dataset?.tag
    if (tag) {
      e.preventDefault()
      e.stopPropagation()
      toggleTag(tag)
    }
  })

  initFromURL()
  render()
})
