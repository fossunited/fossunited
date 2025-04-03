<template>
  <div>
    <label class="text-base text-gray-500">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="flex flex-wrap gap-3 mt-2">
      <div
        v-for="(option, index) in options"
        :key="index"
        class="p-2 flex gap-2 items-center text-sm rounded border text-ink-gray-5 hover:text-ink-gray-6 hover:cursor-pointer hover:border-gray-400 transition-all"
        :class="{ 'text-ink-gray-8 border-gray-800 bg-gray-50': isSelected(option.value) }"
        @click="toggleSelected(option.value)"
      >
        <IconCheck v-if="isSelected(option.value)" size="16" />
        {{ option.label }}
      </div>
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
  return model.value.includes(value)
}

const toggleSelected = (value) => {
  if (isSelected(value)) {
    model.value = model.value.filter((item) => item !== value)
  } else {
    model.value.push(value)
  }
}
</script>
