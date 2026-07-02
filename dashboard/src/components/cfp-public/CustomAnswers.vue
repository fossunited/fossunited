<template>
  <div v-if="answered.length" class="flex flex-col gap-4">
    <h3 class="flex items-center gap-1.5 text-sm font-medium text-ink-gray-5 uppercase">
      <IconMessageCircleQuestion class="w-4 h-4 text-ink-gray-4" />
      Additional Questions
    </h3>
    <div class="flex flex-col gap-4">
      <div v-for="(item, index) in answered" :key="index" class="flex flex-col gap-1.5">
        <span class="text-xs font-medium text-ink-gray-5">{{ item.question }}</span>

        <!-- Response is the highlight: very subtle box -->
        <div class="w-fit max-w-full rounded-md border border-outline-gray-1 bg-surface-gray-1 px-3 py-2">
          <!-- Rich HTML (Text Editor) -->
          <div
            v-if="isRich(item.type)"
            class="prose prose-sm max-w-full text-ink-gray-8"
            v-html="cleanedHTML(item.response)"
          ></div>

          <!-- Checkbox -->
          <span v-else-if="isCheck(item.type)" class="text-sm text-ink-gray-8">
            {{ isTruthy(item.response) ? 'Yes' : 'No' }}
          </span>

          <!-- Long text and plain text/select/radio -->
          <span
            v-else
            class="text-sm text-ink-gray-8 whitespace-pre-wrap"
          >{{ item.response }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { IconMessageCircleQuestion } from '@tabler/icons-vue'
import { cleanedHTML } from '@/helpers/utils'

const props = defineProps({
  answers: {
    type: Array,
    default: () => [],
  },
})

// `type` is stored as the frontend token (text_editor/checkbox/...) but handle
// the doctype literals (Text Editor/Check/...) defensively too.
const isRich = (type) => ['text_editor', 'Text Editor'].includes(type)
const isCheck = (type) => ['checkbox', 'Check'].includes(type)

const isTruthy = (v) => {
  if (v === undefined || v === null) return false
  const s = String(v).trim().toLowerCase()
  return !['', '0', 'false', 'no'].includes(s)
}

const answered = computed(() =>
  (props.answers ?? []).filter((a) => {
    if (isCheck(a.type)) return true
    return a.response !== undefined && a.response !== null && String(a.response).trim() !== ''
  }),
)
</script>
