$(document).ready(function () {
  // Onclick event for Event Cards (not needed anymore)
  // $(".event-card").click(function () {
  // 	window.location.pathname = "/" + $(this).data("route");
  // });

  // Horizontal Navbar Controls for Profile & Event Pages
  setNavbarControl()
  tab_navigation()
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
