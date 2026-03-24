<template>
  <!-- Disqualification Message -->
  <div
    v-if="!isLoading && isDisqualified"
    class="min-h-screen flex items-center justify-center p-4 bg-surface-gray-1"
  >
    <div class="max-w-2xl w-full space-y-6">
      <div class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="h-16 w-16 rounded-full bg-surface-red-1 flex items-center justify-center">
            <IconHandStop class="w-8 h-8 text-surface-red-5" />
          </div>
        </div>
        <div>
          <h2 class="text-2xl font-semibold text-ink-gray-7">Access Denied</h2>
          <p class="mt-2 text-ink-gray-5">
            You have been disqualified from {{ hackathonName }}. You won't be able to participate
            anymore.
          </p>
        </div>
      </div>

      <div
        v-if="rules"
        class="border border-outline-gray-3 rounded-lg p-6 space-y-3 bg-surface-white"
      >
        <h4 class="font-semibold flex items-center gap-2 text-ink-gray-7">
          <IconFileInvoice class="w-5 h-5 text-ink-gray-5" />
          Hackathon Rules
        </h4>
        <div class="prose prose-sm max-w-none text-ink-gray-6" v-html="rules"></div>
      </div>

      <div class="border border-outline-gray-3 rounded-lg p-4 bg-surface-white">
        <p class="text-sm flex items-start gap-2 text-ink-gray-6">
          <IconInfoCircle class="w-5 h-5 flex-shrink-0 mt-0.5 text-surface-blue-3" />
          <span>
            If you believe this is an error, please write to us at fosshack@fossunited.org
          </span>
        </p>
      </div>

      <div class="text-center pt-4">
        <!-- an easter egg awaits.. -->
        <button
          @click="redirectToExternalUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')"
          aria-label="Open external video in a new tab"
          class="px-6 py-2.5 bg-surface-gray-7 text-ink-white rounded-lg font-medium hover:bg-surface-gray-6 transition-colors"
        >
          Better Luck Next Time!
        </button>
      </div>
    </div>
  </div>

  <div
    v-else-if="isLoading"
    class="min-h-screen flex items-center justify-center bg-surface-gray-1"
  >
    <div class="text-center space-y-4">
      <div
        class="h-12 w-12 border-b-2 border-surface-gray-7 rounded-full animate-spin mx-auto"
      ></div>
      <p class="text-ink-gray-5">Loading...</p>
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
import { redirectToExternalUrl } from '@/helpers/utils'

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
