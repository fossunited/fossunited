<template>
  <div class="flex gap-2 items-center">
    <FossClubIcon />
    <span class="text-base font-medium">{{ name }}</span>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import FossClubIcon from '@/components/icons/FossClubIcon.vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
})
</script>
