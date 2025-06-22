<script setup>
import Drawer from '@/components/ui/Drawer.vue'
import SubmissionDetails from './SubmissionDetails.vue'

const show = defineModel('show', { type: Boolean })
const submissionId = defineModel('submissionId', { type: String, default: '' })
</script>
<template>
  <Drawer v-model="show" title="Submission Details">
    <SubmissionDetails :submission-id="submissionId" />
  </Drawer>
</template>
