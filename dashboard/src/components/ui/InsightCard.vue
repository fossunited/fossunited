<script setup>
defineProps({
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  value: {
    type: String,
    default: '',
  },
  theme: {
    type: String,
    default: 'gray',
  },
  isActive: {
    type: Boolean,
    default: false,
  },
})
</script>
<template>
  <div
    class="bg-surface-base flex flex-col gap-4 justify-between border rounded-4 p-4 cursor-pointer hover:bg-surface-gray-1 transition-colors"
    :class="{ 'ring-2 ring-inset ring-outline-gray-3 bg-surface-gray-1': isActive }"
  >
    <div class="flex flex-col gap-4">
      <slot name="title">
        <span class="text-sm text-ink-gray-5">{{ title }}</span>
      </slot>
      <slot name="value">
        <div class="flex gap-2 items-end">
          <span class="text-3xl-semibold">{{ value }}</span>
          <slot name="post-value"></slot>
        </div>
      </slot>
    </div>
    <slot name="description">
      <span v-if="description" class="text-sm text-ink-gray-5">{{ description }}</span>
    </slot>
  </div>
</template>
