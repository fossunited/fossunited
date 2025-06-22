<script setup>
import SubmissionListItem from './SubmissionListItem.vue'
const submissions = defineModel({ type: Array, required: true })
</script>
<template>
  <div class="flex flex-col gap-2 w-full">
    <SubmissionListItem
      v-for="submission in submissions"
      :key="submission.name"
      :submission="submission"
    >
    </SubmissionListItem>
  </div>
</template>
