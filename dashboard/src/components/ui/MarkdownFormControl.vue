<template>
  <div class="flex flex-col gap-1.5">
    <div class="flex items-center justify-between gap-2">
      <FormLabel v-if="label" :label="label" />
      <div
        class="flex rounded-5 border border-outline-gray-2 overflow-hidden shrink-0"
        role="tablist"
        :aria-label="label ? `${label} view` : 'Editor view'"
      >
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'write'"
          class="px-2.5 py-1 text-xs font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-5"
          :class="
            mode === 'write'
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-5 hover:text-ink-gray-7'
          "
          @click="mode = 'write'"
        >
          Write
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'preview'"
          class="px-2.5 py-1 text-xs font-medium border-l border-outline-gray-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-5"
          :class="
            mode === 'preview'
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-5 hover:text-ink-gray-7'
          "
          @click="mode = 'preview'"
        >
          Preview
        </button>
      </div>
    </div>

    <Textarea
      v-if="mode === 'write'"
      v-model="model"
      :size="size"
      variant="subtle"
      :rows="rows"
      :placeholder="placeholder"
    />
    <div
      v-else
      class="prose prose-sm max-w-full p-2.5 border rounded-4 border-outline-gray-2 bg-surface-gray-1 dark:bg-surface-gray-2 dark:prose-invert overflow-auto"
      :style="{ minHeight: `${rows * 1.5}rem` }"
    >
      <div v-if="renderedHtml" v-html="renderedHtml" />
      <p v-else class="text-ink-gray-4 italic m-0">Nothing to preview yet.</p>
    </div>

    <p v-if="description" class="text-xs text-ink-gray-5">{{ description }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormLabel, Textarea } from 'frappe-ui'
import { markdownToHTML } from '@/helpers/markdown'
import DOMPurify from 'dompurify'

defineProps({
  label: { type: String, default: '' },
  description: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  size: { type: String, default: 'md' },
  rows: { type: Number, default: 8 },
})

const model = defineModel({ type: String, default: '' })

const mode = ref('write')

// Same render path the public schedule page uses to display this markdown --
// keeps the preview honest about what readers will actually see.
const renderedHtml = computed(() =>
  model.value?.trim() ? DOMPurify.sanitize(markdownToHTML(model.value)) : '',
)
</script>
