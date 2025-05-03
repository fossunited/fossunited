<template>
  <RadioGroup v-model="value" class="flex flex-col gap-2">
    <RadioGroupLabel class="text-base text-gray-500">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </RadioGroupLabel>
    <div class="grid gap-4" :class="options.length > 4 ? 'md:grid-cols-3' : 'md:grid-flow-col'">
      <RadioGroupOption
        v-for="option in options"
        :key="option.value"
        v-slot="{ active, checked }"
        tabindex="0"
        :value="option.value"
        class="flex p-4 gap-2 items-center rounded border border-gray-200 text-gray-600 cursor-pointer hover:border-gray-400 transition-all focus:outline-none focus:ring-2 focus:ring-gray-500"
        :class="{
          'bg-gray-100': active,
          'bg-gray-50 !border-gray-900 !text-gray-900': checked,
        }"
      >
        <component
          :is="checked ? IconCircleCheckFilled : IconCircle"
          class="shrink-0"
          :class="{ 'fill-gray-900': checked }"
          size="20"
        />
        <div class="flex flex-col gap-1">
          <span class="text-base">{{ option.label }}</span>
          <span v-if="option.description" class="text-sm">{{ option.description }}</span>
        </div>
        <Tooltip v-if="option.help" :text="option.help">
          <IconHelpCircleFilled class="fill-gray-900" size="20" />
        </Tooltip>
      </RadioGroupOption>
    </div>
  </RadioGroup>
</template>

<script setup>
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'
import { defineProps } from 'vue'
import { IconCircle, IconCircleCheckFilled, IconHelpCircleFilled } from '@tabler/icons-vue'
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
})

const value = defineModel({ type: String, required: true })
</script>
