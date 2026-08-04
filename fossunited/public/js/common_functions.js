// file bundled directly in website.bundle.js

$(document).ready(function () {
  // Onclick event for Event Cards (not needed anymore)
  // $(".event-card").click(function () {
  //    window.location.pathname = "/" + $(this).data("route");
  // });

  // Horizontal Navbar Controls for Profile & Event Pages
  setNavbarControl()
  tab_navigation()

  // Global BS4 tooltip/popover opt-in: any element with data-toggle="tooltip"/"popover"
  // gets one. Runs on every page (bundled in website.bundle.js) so pages need no init line.
  // trigger: 'hover focus' (not the BS4 popover default of 'click') so keyboard-focused
  // elements surface the content too — a plain focusable span never auto-fires 'click'
  // on Enter/Space the way a real <button> does, so 'click' alone would lock out keyboard users.
  $('[data-toggle="tooltip"]').tooltip()
  $('[data-toggle="popover"]').popover({ trigger: 'hover focus', html: false })

  initTablistKeyboardNav()
})

function makeQuill(
  id,
  toolbarOptions = [
    [{ header: [1, 2, 3, 4, 5, 6, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    ['blockquote', 'code-block'],
    [{ list: 'ordered' }, { list: 'bullet' }],
    [{ script: 'sub' }, { script: 'super' }],
    [{ indent: '-1' }, { indent: '+1' }],
    [{ direction: 'rtl' }],
    [{ color: [] }, { background: [] }],
    [{ align: [] }],
    ['clean'],
  ],
) {
  // eslint-disable-next-line no-undef
  let quill = new Quill(`${id}`, {
    modules: {
      toolbar: toolbarOptions,
    },
    theme: 'snow',
  })
  return quill
}

function setNavbarControl() {
  let navItems = document.querySelectorAll('.horizontal-navbar--item')
  let contentDivs = document.querySelectorAll('.content-div')
  let activeNavItem = navItems[0]
  let activeContentDiv = contentDivs[0]

  if (navItems.length === 0 || contentDivs.length === 0) return

  contentDivs.forEach((contentDiv) => {
    contentDiv.classList.add('hide')
  })
  activeContentDiv.classList.remove('hide')
  activeNavItem.classList.add('active')

  navItems.forEach((navItem) => {
    navItem.addEventListener('click', () => {
      activeNavItem.classList.remove('active')
      activeContentDiv.classList.add('hide')
      navItem.classList.add('active')
      activeNavItem = navItem
      activeContentDiv = document.querySelector(`#${navItem.id.split('-')[0]}`)
      activeContentDiv.classList.remove('hide')
    })
  })
}

function publish_form(e) {
  let doctype = $(e).data('doctype')
  let docname = $(e).data('docname')
  let parent = $(e).data('parent')
  frappe.call({
    method: 'fossunited.fossunited.forms.publish_form',
    args: {
      doctype: doctype,
      docname: docname,
    },
    callback: (r) => {
      $(`#${parent}`).load(window.location.href + ` #${parent}`)
    },
    error: (e) => {
      frappe.msgprint(e.message)
    },
  })
}

function tab_navigation() {
  let url = new URL(window.location.href)
  let tab = url.searchParams.get('tab')
  if (!tab) return // if no tab is specified, no action
  let tabControl = document.getElementById(`${tab}-nav-item`)

  if (tabControl) {
    tabControl.click()
  }
}

// APG tablist keyboard pattern (arrow keys move + activate, roving tabindex) for native
// BS4 tabs. Scoped to [data-toggle="tab"]
function initTablistKeyboardNav() {
  document.querySelectorAll('[role="tablist"]').forEach((list) => {
    const tabs = Array.from(list.querySelectorAll('[role="tab"][data-toggle="tab"]'))
    if (!tabs.length) return

    function activate(tab) {
      tabs.forEach((t) => t.setAttribute('tabindex', '-1'))
      tab.setAttribute('tabindex', '0')
      tab.focus()
      $(tab).tab('show')
    }

    list.addEventListener('keydown', (e) => {
      const i = tabs.indexOf(document.activeElement)
      if (i === -1) return
      let next = null
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length]
      else if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length]
      else if (e.key === 'Home') next = tabs[0]
      else if (e.key === 'End') next = tabs[tabs.length - 1]
      if (next) {
        e.preventDefault()
        activate(next)
      }
    })
  })
}

function unpublish_form(e) {
  let doctype = $(e).data('doctype')
  let docname = $(e).data('docname')
  let parent = $(e).data('parent')
  frappe.call({
    method: 'fossunited.fossunited.forms.unpublish_form',
    args: {
      doctype: doctype,
      docname: docname,
    },
    callback: (r) => {
      $(`#${parent}`).load(window.location.href + ` #${parent}`)
    },
    error: (e) => {
      frappe.msgprint(e.message)
    },
  })
}

function validate_mandatory_fields() {
  // get all the input tags which have an attribute of required, and see if they are filled or not
  let inputs = document.querySelectorAll('input[required]')
  let selects = document.querySelectorAll('select[required]')
  let textareas = document.querySelectorAll('textarea[required]')

  // for all input, selects and textareas, check if they are filled or not. If they are not filled or selected then return false with message to fill that field
  let messages = []

  for (let input of inputs) {
    if (input.value === '') {
      let label = document.querySelector(`label[for="${input.id}"]`)
      let labelText = label ? label.innerText : input.name
      messages.push(`<strong>${labelText}</strong> is a required field.<br>`)
    }
  }

  for (let select of selects) {
    if (select.value === '') {
      let label = document.querySelector(`label[for="${select.id}"]`)
      let labelText = label ? label.innerText : select.name
      messages.push(`<strong>${labelText}</strong> is a required field.<br>`)
    }
  }

  for (let textarea of textareas) {
    if (textarea.value === '') {
      let label = document.querySelector(`label[for="${textarea.id}"]`)
      let labelText = label ? label.innerText : textarea.name
      messages.push(`<strong>${labelText}</strong> is a required field.<br>`)
    }
  }

  if (messages.length > 0) {
    frappe.msgprint(messages.join('\n'))
    return false
  }

  return true
}

function check_if_logged_in(message = 'You need to be logged in to perform this action.') {
  if (frappe.session.user == 'Guest') {
    frappe.msgprint({
      title: __('Login Required'),
      message: message + '<hr> Redirecting to login page in 7 seconds.',
      primary_action: {
        action: () => {
          window.location.href = `/login?redirect-to=${window.location.pathname}`
        },
        label: __('Go to Login'),
      },
    })
    setTimeout(() => {
      window.location.href = `/login?redirect-to=${window.location.pathname}`
    }, 7000)
    return false
  }
  return true
}

function check_if_profile_complete() {
  frappe
    .call({
      method: 'fossunited.fossunited.utils.validate_profile_completion',
    })
    .then((r) => {
      if (!r.message) {
        frappe.msgprint({
          title: __('FOSS Profile Required!'),
          message: __(
            'You need to complete your profile to access this form. <br> Redirecting in 7 seconds.',
          ),
          primary_action: {
            action: () => {
              window.location.href = `/create-foss-profile?redirect-to=${window.location.pathname}`
            },
            label: __('Complete your profile ->'),
          },
        })
        setTimeout(() => {
          window.location.href = `/create-foss-profile?redirect-to=${window.location.pathname}`
        }, 7000)
        return false
      }
      return true
    })
}

function set_mandatory_asterisk() {
  // for every required input, textarea and select, add a red asterisk after their label. Wrap the label in a span to do this
  $('input[required], textarea[required], select[required], .ql-editor-custom[required]').each(
    (idx, element) => {
      let label = $(element).prev('label')
      if ($(element).data('type') == 'Check') {
        label = $(element).next('label')
      }
      if ($(element).hasClass('ql-editor-custom')) {
        label = $(element).prev('div').prev('div')
      }

      label.html(`<span>${label.html()}</span>`)
      label.find('span').append('<span class="text-danger">*</span>')
    },
  )
}

function copyLinkToClipboard(e) {
  let link = window.location.origin + '/' + $(e).data('url')
  navigator.clipboard.writeText(link)
  $('.tooltip-text').text('Link Copied!')
}

function resetTooltip() {
  $('.tooltip-text').html('Copy Link')
}

document.addEventListener('DOMContentLoaded', () => {
  const toggles = document.querySelectorAll('.theme-toggle')
  if (!toggles.length) return document.documentElement.setAttribute('data-theme', 'light')
  const savedTheme = localStorage.getItem('theme')
  document.documentElement.setAttribute(
    'data-theme',
    savedTheme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
  )
  toggles.forEach((toggle) => {
    const icon = toggle.querySelector('i')
    const lightIcon = toggle.dataset.lightIcon || 'ti-moon'
    const darkIcon = toggle.dataset.darkIcon || 'ti-sun'

    updateIcon()

    toggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme')
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', newTheme)
      document.documentElement.setAttribute('data-theme', newTheme)
      updateAllIcons()
    })

    function updateIcon() {
      const theme = document.documentElement.getAttribute('data-theme')
      icon.className = `ti ${theme === 'dark' ? darkIcon : lightIcon}`
    }

    function updateAllIcons() {
      const theme = document.documentElement.getAttribute('data-theme')
      toggles.forEach((btn) => {
        const ic = btn.querySelector('i')
        const li = btn.dataset.lightIcon || 'ti-moon'
        const di = btn.dataset.darkIcon || 'ti-sun'
        ic.className = `ti ${theme === 'dark' ? di : li}`
      })
    }
  })
})

// "2025-12-29" -> "Monday, December 29, 2025"
function formatFullDate(dateInput, locale = 'en-IN') {
  if (!dateInput) return ''

  const date = dateInput instanceof Date ? dateInput : new Date(dateInput)
  if (isNaN(date)) return ''

  return date.toLocaleDateString(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// "2025-12-29T14:30:45" -> "02:30:45 PM"
function formatTimeOnly(dateInput, locale = 'en-IN') {
  if (!dateInput) return ''

  const date = dateInput instanceof Date ? dateInput : new Date(dateInput)
  if (isNaN(date)) return ''

  return date.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatShortDate(dateInput, locale = 'en-IN') {
  if (!dateInput) return ''

  const date = dateInput instanceof Date ? dateInput : new Date(dateInput)
  if (isNaN(date)) return ''

  return date.toLocaleDateString(locale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function truncateStr(title, len) {
  if (!title) return ''
  return title.length > len ? title.substring(0, len) + '...' : title
}

function toggleSection(id) {
  const content = document.getElementById(id)
  if (!content) return
  const header = content?.previousElementSibling
  content.classList.toggle('hidden')
  header?.querySelector('.v3-toggle-icon')?.classList.toggle('rotated')
  header?.setAttribute('aria-expanded', !content.classList.contains('hidden'))
}

// Debounce: delay fn until `wait` ms after the last call. Used by search inputs.
function debounce(fn, wait = 250) {
  let t
  return function (...args) {
    clearTimeout(t)
    t = setTimeout(() => fn.apply(this, args), wait)
  }
}

// Pagination window: array of page numbers with '…' gaps. First, last, and
// current +/- `spread` are always shown. e.g. buildPageWindow(5, 20) ->
// [1,'…',4,5,6,'…',20]. Render each as a button; skip '…'.
function buildPageWindow(page, totalPages, spread = 1) {
  const win = []
  for (let p = 1; p <= totalPages; p++) {
    if (p === 1 || p === totalPages || Math.abs(p - page) <= spread) win.push(p)
    else if (win[win.length - 1] !== '…') win.push('…')
  }
  return win
}

// Read the current query string as a plain object. getParams().foo -> "bar".
function getParams() {
  return Object.fromEntries(new URLSearchParams(window.location.search))
}

// Write params to the URL without a reload. Falsy values are dropped.
// setParams({q: 'x', page: 1}) -> "?q=x&page=1"; setParams({}) clears them.
function setParams(obj) {
  const p = new URLSearchParams()
  Object.entries(obj).forEach(([k, v]) => {
    if (v !== '' && v != null && v !== false) p.set(k, v)
  })
  const qs = p.toString()
  history.replaceState(null, '', qs ? `${location.pathname}?${qs}` : location.pathname)
}

// expose all globally via window
Object.assign(window, {
  makeQuill,
  setNavbarControl,
  publish_form,
  tab_navigation,
  initTablistKeyboardNav,
  unpublish_form,
  validate_mandatory_fields,
  check_if_logged_in,
  check_if_profile_complete,
  set_mandatory_asterisk,
  copyLinkToClipboard,
  resetTooltip,
  formatFullDate,
  formatTimeOnly,
  formatShortDate,
  truncateStr,
  toggleSection,
  debounce,
  buildPageWindow,
  getParams,
  setParams,
})
