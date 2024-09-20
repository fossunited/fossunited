<template>
  <div
    class="border-b pb-1 flex flex-col gap-1 group focus-within:border-gray-800 transition-colors"
  >
    <div class="flex gap-1">
      <slot name="label-prefix"></slot>
      <div v-if="label" class="text-sm text-gray-600">
        <span>
          {{ label }}
        </span>
        <span v-if="required">*</span>
      </div>
    </div>
    <div class="flex gap-1 items-center">
      <slot name="input-prefix"></slot>
      <input
        v-model="model"
        :placeholder="placeholder"
        class="focus:border-none focus:ring-0 border-none p-0 uppercase w-full"
        :type="type"
        :class="inputClasses"
      />
    </div>
    <small v-if="description" class="text-gray-600">
      {{ description }}
    </small>
  </div>
</template>
<script setup>
import { defineModel, defineProps } from 'vue'

const model = defineModel({
  type: [String, Number, Boolean, Object, Array],
  default: '',
})

const props = defineProps({
  type: {
    type: String,
    default: 'text',
  },
  label: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  inputClasses: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
})
</script>
