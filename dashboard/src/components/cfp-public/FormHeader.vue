<template>
  <div class="flex flex-col gap-2 text-black">
    <h1 class="text-3xl font-bold">Proposal Submission Form</h1>
    <div class="prose max-w-full" v-html="_description"></div>
  </div>
</template>

<script setup>
import { inject, computed } from 'vue'
import { cleanedHTML } from '@/helpers/utils'

const cfpData = inject('$cfpData')

const _description = computed(() => {
  return cleanedHTML(cfpData.data.cfp_form_description)
})
</script>
