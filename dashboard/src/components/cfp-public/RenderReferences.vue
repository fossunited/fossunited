<template>
  <div class="space-y-2">
    <label class="text-base font-medium text-gray-600">References</label>
    <div
      v-for="(reference, index) in references"
      :key="index"
      class="flex gap-2 items-center text-base text-gray-600 hover:cursor-pointer hover:text-gray-800 transition-colors"
    >
      <IconLink class="w-4 h-4" />
      <a :href="reference.link" target="_blank">
        {{ reference.link }}
      </a>
    </div>
  </div>
</template>
<script setup>
import { IconLink } from '@tabler/icons-vue'
defineProps({
  references: {
    type: Array,
    required: true,
  },
})
</script>
