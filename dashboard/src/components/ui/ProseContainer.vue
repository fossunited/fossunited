<template>
  <div class="flex flex-col my-1">
    <label class="text-base font-medium text-ink-gray-5 -mb-3 px-2 bg-surface-white z-10 w-fit ml-2">
      {{ label }}
    </label>
    <div
      class="prose prose-sm prose-h1:text-xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base prose-h5:text-sm prose-h1:font-semibold prose-h2:font-semibold prose-h3:font-semibold prose-h4:font-medium prose-h5:font-medium max-w-full p-4 border rounded border-outline-gray-3"
      v-html="cleanedHTML(value)"
    ></div>
  </div>
</template>
<script setup>
import { cleanedHTML } from '@/helpers/utils'

defineProps({
  label: {
    type: String,
    default: '',
  },
  value: {
    type: String,
    default: '',
  },
})
</script>
