<template>
  <a
    v-if="visible"
    :href="docsUrl"
    target="_blank"
    rel="noopener noreferrer"
    class="relative my-4 inline-flex self-start items-center gap-1 p-2 pr-8 rounded bg-surface-blue-1 border-2 border-dashed border-outline-blue-1 text-sm hover:bg-surface-blue-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
  >
    <IconBook2 class="w-6 h-6 flex-shrink-0" />

    <slot>
      {{ message }}
    </slot>

    <span class="text-ink-blue-2 ml-1">
      {{ docsLabel }}
    </span>

    <button
      type="button"
      class="absolute top-1 right-1 text-ink-blue-2 hover:text-ink-blue-3"
      aria-label="Close"
      @click.stop.prevent="visible = false"
    >
      ✕
    </button>
  </a>
</template>

<script setup>
import { ref } from 'vue'
import { IconBook2 } from '@tabler/icons-vue'

const visible = ref(true)

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
