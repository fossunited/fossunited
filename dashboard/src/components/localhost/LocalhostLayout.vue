<template>
  <Dialog
    :model-value="showDialog"
    class="z-50"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
    @update:model-value="$emit('update:showDialog', $event)"
  />
  <Header />
  <div v-if="isValidated" class="w-full p-4 flex items-center justify-center">
    <div class="max-w-screen-xl w-full">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { Dialog } from 'frappe-ui'
import Header from '@/components/Header.vue'

defineProps({
  isValidated: {
    type: Boolean,
    required: true,
  },
  showDialog: {
    type: Boolean,
    required: true,
  },
  dialogMessage: {
    type: String,
    default: '',
  },
})

defineEmits(['update:showDialog'])
</script>
