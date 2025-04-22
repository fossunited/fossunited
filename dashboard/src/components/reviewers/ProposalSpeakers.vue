<template>
  <div class="flex flex-col gap-4">
    <ProposalSpeakerCard v-for="speaker in speakers" :key="speaker.name" :speaker="speaker" />
  </div>
</template>
<script setup>
import ProposalSpeakerCard from './ProposalSpeakerCard.vue'

defineProps({
  speakers: {
    type: Array,
    required: true,
  },
})
</script>
