<template>
  <div>
    <label class="text-base text-ink-gray-4">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="flex flex-wrap gap-3 mt-2">
      <div
        v-for="(option, index) in options"
        :key="index"
        class="p-2 flex gap-2 items-center text-sm rounded border text-ink-gray-5 hover:text-ink-gray-6 hover:cursor-pointer hover:border-outline-gray-3 transition-all"
        :class="{ 'text-ink-gray-8 border-outline-gray-5 bg-surface-gray-1': isSelected(option.value) }"
        @click="toggleSelected(option.value)"
      >
        <IconCheck v-if="isSelected(option.value)" size="16" />
        {{ option.label }}
      </div>
    </div>
    <div v-if="required && (!model || model.length === 0)" class="mt-1 text-sm text-red-500">
      Please select at least one option
    </div>
  </div>
</template>
<script setup>
import { IconCheck } from '@tabler/icons-vue'
import { FormControl } from 'frappe-ui'

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
