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
      return 'border-outline-blue-1 bg-surface-blue-1 text-ink-blue-2'
    case 'success':
      return 'border-outline-green-1 bg-surface-green-1 text-ink-green-3'
    case 'warning':
      return 'border-outline-amber-1 bg-surface-amber-1 text-yellow-600'
    case 'error':
      return 'border-outline-red-1 bg-surface-red-1 text-ink-red-4'
    case 'simple':
      return 'border-outline-gray-2 bg-surface-gray-1 text-ink-gray-5'
    case 'dark':
      return 'border-outline-gray-5 bg-surface-gray-6 text-ink-white'
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
