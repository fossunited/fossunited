<script setup>
import ProseContainer from '@/components/ui/ProseContainer.vue'
import RenderReferences from '@/components/cfp-public/RenderReferences.vue'
import RenderSessionCategories from '@/components/cfp-public/RenderSessionCategories.vue'
import { computed, inject } from 'vue'

const submission = inject('curr_submission')

const getCategories = computed(() => {
  if (!submission.data.session_categories) {
    return []
  }

  return submission.data.session_categories.split('\n')
})
</script>
<template>
  <div class="flex flex-col gap-4">
    <ProseContainer label="Session Description" :value="submission.data.talk_description" />
    <ProseContainer label="Key Takeaways" :value="submission.data.key_takeaways" />
    <RenderReferences :references="submission.data.references" />
    <RenderSessionCategories :categories="getCategories" />
  </div>
</template>
