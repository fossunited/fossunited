<template>
  <RadioGroup v-model="value" class="flex flex-col gap-2">
    <RadioGroupLabel class="text-base text-ink-gray-4">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </RadioGroupLabel>
    <small v-if="description" class="text-sm text-ink-gray-5">{{ description }}</small>
    <div class="grid gap-4" :class="options.length > 4 ? 'md:grid-cols-3' : 'md:grid-flow-col'">
      <RadioGroupOption
        v-for="option in options"
        :key="option.value"
        v-slot="{ active, checked }"
        tabindex="0"
        :value="option.value"
        class="flex p-4 gap-2 items-center rounded border border-outline-gray-1 text-ink-gray-5 cursor-pointer hover:border-outline-gray-3 transition-all focus:outline-none focus:ring-2 focus:ring-gray-500"
        :class="{
          'bg-surface-gray-2': active,
          'bg-surface-gray-1 border-outline-gray-5 text-ink-gray-9': checked,
        }"
      >
        <component
          :is="checked ? IconCircleCheckFilled : IconCircle"
          class="shrink-0"
          :class="{ 'text-ink-gray-9 ring-gray-500': checked }"
          size="20"
        />
        <div class="flex flex-col gap-1">
          <span class="text-base">{{ option.label }}</span>
          <span v-if="option.description" class="text-sm">{{ option.description }}</span>
        </div>
        <Tooltip v-if="option.help" :text="option.help">
          <IconHelp class="text-ink-gray-9" size="20" />
        </Tooltip>
      </RadioGroupOption>
    </div>
  </RadioGroup>
</template>

<script setup>
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'
import { defineProps } from 'vue'
import { IconCircle, IconCircleCheckFilled, IconHelp } from '@tabler/icons-vue'
import { Tooltip } from 'frappe-ui'

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
  modelValue: {
    type: [String, Number],
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
})

const value = defineModel({ type: String, required: true })
</script>
