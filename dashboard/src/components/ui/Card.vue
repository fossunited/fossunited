<template>
  <!--
    Local replacement for frappe-ui 0.1.x's `Card`, which 1.0 removed with no
    successor. Same props and slots (title, subtitle, loading, #actions,
    #actions-left, default) so consumers did not need template changes.
    Token names are the pre-tokens-v2 spellings used everywhere else in the
    app, so the `tokens-v2` codemod renames them along with the rest.
  -->
  <div class="flex flex-col rounded-lg border bg-surface-cards px-6 py-5 shadow">
    <div class="flex items-baseline justify-between">
      <div class="flex items-baseline space-x-2">
        <div v-if="$slots['actions-left']" class="flex items-center space-x-2">
          <slot name="actions-left" />
        </div>
        <h2 v-if="title" class="text-xl font-semibold text-ink-gray-9">{{ title }}</h2>
      </div>
      <div v-if="$slots['actions']" class="flex items-center space-x-2">
        <slot name="actions" />
      </div>
    </div>
    <p v-if="subtitle" class="mt-1.5 text-base text-ink-gray-7 dark:text-ink-gray-8">
      {{ subtitle }}
    </p>
    <div v-if="loading" class="mt-4 flex flex-auto flex-col items-center justify-center rounded-md">
      <LoadingText />
    </div>
    <div v-else-if="$slots['default']" class="mt-4 flex-auto overflow-auto">
      <slot />
    </div>
  </div>
</template>
<script setup>
import { LoadingText } from 'frappe-ui'

defineProps({
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})
</script>
