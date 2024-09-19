<!-- StyledSelect.vue -->
<template>
  <div class="relative">
    <Select v-bind="$attrs" :class="selectClasses" />
    <div class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
      <ChevronDown />
    </div>
  </div>
</template>

<script setup>
import { Select } from 'frappe-ui'
import ChevronDown from '@/components/icons/ChevronDown.vue'

const selectClasses = `
  w-50 h-10 !p-2 !pr-10 !px-3
  rounded-sm
  border border-gray-900 bg-gray-900 text-gray-100
  hover:bg-gray-800 hover:border-gray-800
  focus:outline-none focus-visible:ring-1 focus-visible:ring-gray-400
  transition-colors
`
</script>
