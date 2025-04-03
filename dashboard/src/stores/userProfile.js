import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const useUserProfileStore = defineStore('userProfile', () => {
  console.log('UserProfileStore created!')

  const profileFetched = ref(false)

  const profile = createResource({
    url: 'fossunited.api.dashboard.get_session_user_profile',
    auto: false,
    headers: {
      'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
    },
    onSuccess(data) {
      console.log('User profile fetched successfully:', data)
      profileFetched.value = true
    },
    onError(error) {
      console.error('Failed to fetch user profile:', error)
    },
  })

  const fetchProfile = async () => {
    if ((!profileFetched.value || profile.error) && !profile.loading) {
      console.log('Pinia Store: Initiating profile fetch...')
      try {
        await profile.fetch()
      } catch (e) {
        console.error('Pinia Store: Error during profile.fetch() call:', e)
      }
    } else if (profile.loading) {
      console.log('Pinia Store: Profile fetch already in progress, skipping duplicate call.')
    } else if (profileFetched.value) {
      console.log('Pinia Store: Profile already fetched, serving from store.')
    }
    return profile.data
  }

  return { profile, fetchProfile }
})
