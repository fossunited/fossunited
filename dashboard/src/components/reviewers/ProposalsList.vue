<script setup>
import SubmissionsList from '@/components/event/cfp/SubmissionsList.vue'

defineProps({
  event: { type: String, required: true },
})
defineEmits(['open:submission'])
</script>

<template>
  <SubmissionsList :event="event" reviewer-mode @open:submission="$emit('open:submission', $event)" />
</template>
