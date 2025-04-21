<template>
  <Drawer v-model="show" title="Proposal Details">
    <ProposalDetails v-model:submission-id="submissionId" />
  </Drawer>
</template>
<script setup>
import Drawer from '@/components/ui/Drawer.vue'
import ProposalDetails from './ProposalDetails.vue'

const show = defineModel('show', { type: Boolean })
const submissionId = defineModel('submissionId', { type: String, default: '' })
</script>
