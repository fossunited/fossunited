import router from '@/router'
import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let _sessionUser = cookies.get('user_id')
  if (_sessionUser === 'Guest') {
    _sessionUser = null
  }
  return _sessionUser
}

export const sessionProfileResource = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

let _profileFetchPromise = null
export function fetchSessionProfile() {
  if (!session.isLoggedIn || session.user === 'Guest' || session.user === 'Administrator') {
    return Promise.resolve(null)
  }
  if (sessionProfileResource.data) return Promise.resolve(sessionProfileResource.data)
  if (_profileFetchPromise) return _profileFetchPromise

  _profileFetchPromise = sessionProfileResource.fetch().finally(() => {
    _profileFetchPromise = null
  })
  return _profileFetchPromise
}

export const session = reactive({
  login: createResource({
    url: 'login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
      }
    },
    onSuccess(data) {
      userResource.reload()
      session.user = sessionUser()
      session.login.reset()
      router.replace(data.default_route || '/')
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      userResource.reset()
      sessionProfileResource.reset()
      session.user = sessionUser()
      window.location.href = `/login?redirect-to=/dashboard`
    },
  }),
  user: sessionUser(),
  isLoggedIn: computed(() => !!session.user),
})
