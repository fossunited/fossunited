<script setup>
import ProseContainer from '@/components/ui/ProseContainer.vue'
import RenderReferences from '@/components/cfp-public/RenderReferences.vue'
import RenderSessionCategories from '@/components/cfp-public/RenderSessionCategories.vue'
import { IconScale } from '@tabler/icons-vue'
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
    <div v-if="submission.data.talk_license" class="flex flex-col gap-1">
      <span class="text-xs font-medium text-ink-gray-5 uppercase">License</span>
      <div class="flex items-center gap-1.5 text-sm text-ink-gray-7">
        <IconScale class="w-4 h-4 text-ink-gray-4 flex-shrink-0" />
        <span>{{ submission.data.talk_license }}</span>
      </div>
    </div>
  </div>
</template>
