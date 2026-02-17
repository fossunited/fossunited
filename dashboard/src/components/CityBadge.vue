<template>
  <div class="pl-1 pr-2 py-1 bg-surface-gray-7 text-ink-white flex gap-2 items-center">
    <FossUnitedLogo class="h-8 w-8 p-1 bg-surface-white" />
    <span class="font-fff text-xs uppercase">{{ name }}</span>
  </div>
</template>
<script setup>
import FossUnitedLogo from '@/components/icons/FossUnitedLogo.vue'
import { defineProps } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
})
</script>
