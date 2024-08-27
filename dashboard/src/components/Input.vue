<template>
  <div
    class="border-b pb-1 flex flex-col gap-1 group focus-within:border-gray-800 transition-colors"
  >
    <div class="flex gap-1">
      <slot name="label-prefix"></slot>
      <div class="text-sm text-gray-600" v-if="label">
        <span>
        {{ label }}
        </span>
        <span v-if="required">*</span>
      </div>
    </div>
    <div class="flex gap-1 items-center">
      <slot name="input-prefix"></slot>
      <input
        :placeholder="placeholder"
        class="focus:border-none focus:ring-0 border-none p-0 uppercase w-full"
        :type="type"
        v-model="model"
        :class="inputClasses"
      />
    </div>
    <small class="text-gray-600" v-if="description">
      {{ description }}
    </small>
  </div>
</template>
<script setup>
import { defineModel, defineProps } from 'vue'

const model = defineModel()

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
