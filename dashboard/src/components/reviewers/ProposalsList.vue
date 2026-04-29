<script setup>
import { ref } from 'vue'
import SubmissionsList from '@/components/event/cfp/SubmissionsList.vue'

defineProps({
  event: { type: String, required: true },
})
defineEmits(['open:submission'])
const listRef = ref(null)
defineExpose({
  reloadSubmissions: () => listRef.value?.reloadSubmissions(),
  getNextSubmission: (id) => listRef.value?.getNextSubmission(id)
})
</script>

<template>
  <SubmissionsList ref="listRef" :event="event" reviewer-mode @open:submission="$emit('open:submission', $event)" />
</template>
