<template>
  <!-- Disqualification Message -->
  <div
    v-if="!isLoading && isDisqualified"
    class="w-full min-h-screen flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900"
  >
    <div class="w-full max-w-2xl">
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <div
          class="bg-red-50 dark:bg-red-900/20 border-b border-red-100 dark:border-red-800 px-6 py-8"
        >
          <div class="flex flex-col items-center text-center">
            <div
              class="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/40 mb-4"
            >
              <IconHandStop class="w-5 h-5 text-red-500" />
            </div>
            <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">Access Denied</h2>
            <p class="mt-2 text-base text-gray-600 dark:text-gray-400">
              You have been disqualified from {{ hackathonName }}. You won't be able to participate
              anymore.
            </p>
          </div>
        </div>

        <div class="px-6 py-6 space-y-6">
          <div
            v-if="rules"
            class="bg-amber-50 dark:bg-amber-900/10 rounded-lg p-4 border border-amber-200 dark:border-amber-800"
          >
            <h4
              class="text-sm font-semibold text-amber-900 dark:text-amber-300 mb-3 flex items-center gap-2"
            >
              <IconFileInvoice class="w-5 h-5 text-amber-500" />
              Hackathon Rules
            </h4>
            <div
              class="prose prose-sm dark:prose-invert max-w-none text-amber-900 dark:text-amber-200"
              v-html="rules"
            ></div>
          </div>

          <div
            class="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-4 border border-blue-200 dark:border-blue-800"
          >
            <p class="text-sm text-blue-900 dark:text-blue-300 flex items-start gap-2">
              <IconInfoCircle class="w-5 h-5 text-blue-500" />
              <span>
                If you believe this is an error, please write to us at fosshack@fossunited.org
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    v-else-if="isLoading"
    class="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900"
  >
    <div class="text-center">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100 mx-auto"
      ></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  </div>

  <div v-else-if="isValidated">
    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { IconInfoCircle, IconHandStop, IconFileInvoice } from '@tabler/icons-vue'

const route = useRoute()

const isLoading = ref(true)
const isValidated = ref(false)
const isDisqualified = ref(false)
const hackathonName = ref('')
const rules = ref('')

async function checkDisqualification() {
  isLoading.value = true
  const check = createResource({
    url: 'fossunited.api.hackathon.check_participant_disqualification',
    params: {
      hackathon_permalink: route.params.permalink,
    },
    auto: false,
  })

  try {
    await check.fetch()
    const data = check.data

    if (data.is_disqualified) {
      isDisqualified.value = true
      hackathonName.value = data.hackathon_name
      rules.value = data.rules
      isValidated.value = false
    } else {
      isDisqualified.value = false
      isValidated.value = true
    }
  } catch (error) {
    console.error('Error checking disqualification:', error)
    isValidated.value = true
  } finally {
    isLoading.value = false
  }
}

// Re-check when route changes (moving between children)
watch(
  () => route.name,
  () => {
    checkDisqualification()
  },
)

onMounted(() => {
  checkDisqualification()
})
</script>
