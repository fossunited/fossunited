<template>
  <div class="p-8 border border-outline-gray-2 rounded bg-surface-gray-2">
    <h3 class="font-semibold">Important Guidelines</h3>
    <div class="prose max-w-full" v-html="_guidelines"></div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'
import { cleanedHTML } from '@/helpers/utils'
import { computed, inject } from 'vue'

const cfpData = inject('$cfpData')

const globalGuidelines = createResource({
  url: 'fossunited.api.cfp.get_global_cfp_guidelines',
  auto: true,
})

const _guidelines = computed(() => {
  const override = cfpData.data.cfp_form_description
  if (override) return cleanedHTML(override)
  return cleanedHTML(globalGuidelines.data?.guidelines)
})
</script>
