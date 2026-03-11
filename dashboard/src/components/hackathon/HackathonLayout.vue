<template>
  <!-- Disqualification Dialog -->
  <Dialog
    v-model="showDisqualifiedDialog"
    :options="{
      title: 'Access Denied',
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="flex justify-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            Icons
          </div>
        </div>

        <div class="text-center">
          <h3 class="text-xl font-semibold text-gray-900">You Have Been Disqualified</h3>
          <p class="mt-2 text-sm text-gray-600">
            You have been disqualified from
            <span class="font-medium">{{ hackathonName }}</span> and cannot participant anymore.
          </p>
        </div>

        <div v-if="rules" class="rounded-lg bg-red-50 p-4">
          <h4 class="mb-2 text-sm font-semibold text-red-900">Hackathon Rules:</h4>
          <div class="prose prose-sm max-w-none text-red-800" v-html="rules"></div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4 text-center">
          <p class="text-sm text-gray-600">
            We are sure we had given fair warning to keep activity going on as per our rules. If
            you think this is a mistake, please write email to fosshack@fossunited.org
          </p>
        </div>
      </div>
    </template>
  </Dialog>

  <div v-if="isValidated">
    <slot />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Dialog, createResource } from 'frappe-ui'

const route = useRoute()
const router = useRouter()

const isValidated = ref(false)
const showDisqualifiedDialog = ref(false)
const hackathonName = ref('')
const rules = ref('')

async function checkDisqualification() {
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
      hackathonName.value = data.hackathon_name
      rules.value = data.rules
      showDisqualifiedDialog.value = true
      isValidated.value = false
    } else {
      isValidated.value = true
    }
  } catch (error) {
    console.error('Error checking disqualification:', error)
    // Fail open - allow access on error
    isValidated.value = true
  }
}

onMounted(() => {
  checkDisqualification()
})
</script>
