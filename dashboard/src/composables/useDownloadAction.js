import { ref } from 'vue'
import { showError } from '@/helpers/utils'

/**
 * Wraps an async download/file action with a loading flag and a guard
 * against double-clicks firing it again while one is already in flight.
 */
export function useDownloadAction(errorMessage = 'Could not complete download') {
  const loading = ref(false)

  async function run(action) {
    if (loading.value) return
    loading.value = true
    try {
      await action()
    } catch (error) {
      showError(error, errorMessage)
    } finally {
      loading.value = false
    }
  }

  return { loading, run }
}
