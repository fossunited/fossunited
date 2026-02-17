<template>
  <div class="p-8 border border-outline-gray-2 rounded bg-surface-gray-2">
    <h3 class="font-semibold">Important Guidelines</h3>
    <div class="prose max-w-full" v-html="_guidelines"></div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'
import { cleanedHTML } from '@/helpers/utils'
import { ref } from 'vue'

const _guidelines = ref()

const guidelines = createResource({
  url: 'fossunited.api.cfp.get_global_cfp_guidelines',
  auto: true,
  onSuccess(data) {
    _guidelines.value = cleanedHTML(data.guidelines)
  },
})
</script>
