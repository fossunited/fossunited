<template>
  <a
    :href="docsUrl"
    target="_blank"
    rel="noopener noreferrer"
    class="my-4 inline-flex self-start items-center gap-1 p-2 rounded bg-blue-50 border-2 border-dashed border-blue-600 text-sm hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-400"
  >
    <IconBook2 class="w-6 h-6 flex-shrink-0" />

    <slot>
      {{ message }}
    </slot>

    <span class="text-blue-600 ml-1">
      {{ docsLabel }}
    </span>
  </a>
</template>

<script setup>
import { IconBook2 } from '@tabler/icons-vue'

defineProps({
  message: {
    type: String,
    default: '',
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
