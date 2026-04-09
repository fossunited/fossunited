<template>
  <div
    role="group"
    :aria-labelledby="labelId"
    :aria-required="required ? 'true' : undefined"
    :aria-describedby="showError ? errorId : undefined"
  >
    <div :id="labelId" class="text-base text-ink-gray-4">
      {{ label }}
      <span v-if="required" aria-hidden="true" class="text-red-500">*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </div>
    <div class="flex flex-wrap gap-3 mt-2">
      <div
        v-for="(option, index) in options"
        :key="index"
        role="checkbox"
        :aria-checked="isSelected(option.value)"
        tabindex="0"
        class="p-2 flex gap-2 items-center text-sm rounded border text-ink-gray-5 hover:text-ink-gray-6 hover:cursor-pointer hover:border-outline-gray-3 transition-all focus:outline-2 focus:outline-offset-1"
        :class="{ 'text-ink-gray-8 border-outline-gray-5 bg-surface-gray-1': isSelected(option.value) }"
        @click="toggleSelected(option.value)"
        @keydown.space.prevent="toggleSelected(option.value)"
        @keydown.enter.prevent="toggleSelected(option.value)"
      >
        <IconCheck v-if="isSelected(option.value)" aria-hidden="true" size="16" />
        {{ option.label }}
      </div>
    </div>
    <div
      :id="errorId"
      role="alert"
      aria-live="assertive"
      class="mt-1 text-sm text-red-500"
      :class="{ invisible: !showError }"
    >
      Please select at least one option
    </div>
  </div>
</template>
<script setup>
import { computed, getCurrentInstance } from 'vue'
import { IconCheck } from '@tabler/icons-vue'

const uid = getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2, 7)
const labelId = `multiselect-label-${uid}`
const errorId = `multiselect-error-${uid}`

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  required: {
    type: Boolean,
    default: false,
  },
  options: {
    type: Array,
    required: true,
  },
})

const model = defineModel({ type: Array, required: true })

const showError = computed(() => props.required && (!model.value || model.value.length === 0))

const isSelected = (value) => {
  return model.value?.includes(value)
}

const toggleSelected = (value) => {
  if (!model.value) {
    model.value = []
  }

  if (isSelected(value)) {
    model.value = model.value.filter((item) => item !== value)
  } else {
    model.value = [...model.value, value]
  }
}
</script>
