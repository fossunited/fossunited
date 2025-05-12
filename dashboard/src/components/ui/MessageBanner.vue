<template>
  <div :class="containerClasses">
    <slot name="prefix"></slot>
    <span>
      {{ message }}
    </span>
    <slot name="suffix"></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    default: 'info',
    validator: (value) =>
      ['info', 'success', 'warning', 'error', 'simple', 'dark'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
})

const themeClasses = computed(() => {
  switch (props.variant) {
    case 'info':
      return 'border-blue-600 bg-blue-50 text-blue-600'
    case 'success':
      return 'border-green-600 bg-green-50 text-green-600'
    case 'warning':
      return 'border-yellow-600 bg-yellow-50 text-yellow-600'
    case 'error':
      return 'border-red-600 bg-red-50 text-red-600'
    case 'simple':
      return 'border-gray-300 bg-gray-50 text-gray-600'
    case 'dark':
      return 'border-gray-700 bg-gray-800 text-gray-50'
    default:
      return ''
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-xs p-1'
    case 'lg':
      return 'text-base p-3'
    default:
      return 'text-sm p-2'
  }
})

const containerClasses = computed(() => {
  return `w-full flex gap-2 items-center border rounded ${themeClasses.value} ${sizeClasses.value}`
})
</script>
