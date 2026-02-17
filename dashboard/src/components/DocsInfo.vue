<template>
  <a
    :href="docsUrl"
    target="_blank"
    rel="noopener noreferrer"
    class="my-4 inline-flex self-start items-center gap-1 p-2 rounded bg-surface-blue-1 border-2 border-dashed border-outline-blue-1 text-sm hover:bg-surface-blue-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
  >
    <IconBook2 class="w-6 h-6 flex-shrink-0" />

    <slot>
      {{ message }}
    </slot>

    <span class="text-ink-blue-2 ml-1">
      {{ docsLabel }}
    </span>
  </a>
</template>

<script setup>
import { IconBook2 } from '@tabler/icons-vue'

defineProps({
  message: {
    type: String,
    default: 'Please find platform docs this page',
  },
  docsUrl: {
    type: String,
    default: 'https://docs.fossunited.org/',
  },
  docsLabel: {
    type: String,
    default: 'Read more',
  },
})
</script>
