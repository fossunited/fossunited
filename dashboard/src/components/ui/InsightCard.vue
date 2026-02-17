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
})
</script>
<template>
  <div class="bg-surface-white flex flex-col gap-4 justify-between border rounded p-4">
    <div class="flex flex-col gap-4">
      <slot name="title">
        <span class="text-sm font-normal text-ink-gray-5">{{ title }}</span>
      </slot>
      <slot name="value">
        <div class="flex gap-2 items-end">
          <span class="text-2xl font-semibold">{{ value }}</span>
          <slot name="post-value"></slot>
        </div>
      </slot>
    </div>
    <slot name="description">
      <span v-if="description" class="text-sm text-ink-gray-5">{{ description }}</span>
    </slot>
  </div>
</template>
