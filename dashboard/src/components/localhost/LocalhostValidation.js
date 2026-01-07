import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'

export function LocalhostValidation(localhostId, redirectRoute = 'MyLocalhosts') {
  const router = useRouter()
  const isValidated = ref(false)
  const dialogMessage = ref('')
  const showDialog = ref(false)

  const validateSessionUser = (onSuccessCallback) => {
    createResource({
      url: 'fossunited.api.hackathon.validate_user_as_localhost_member',
      params: {
        localhost_id: localhostId,
      },
      auto: true,
      onSuccess(data) {
        isValidated.value = true
        if (onSuccessCallback) {
          onSuccessCallback(data)
        }
      },
      onError(error) {
        isValidated.value = false
        dialogMessage.value = error.messages
        showDialog.value = true
        setTimeout(() => {
          router.push({ name: redirectRoute })
        }, 2000)
      },
    })
  }

  return {
    isValidated,
    dialogMessage,
    showDialog,
    validateSessionUser,
  }
}
