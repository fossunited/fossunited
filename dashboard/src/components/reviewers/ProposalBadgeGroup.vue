<template>
  <div class="flex flex-wrap gap-2">
    <Badge :label="sessionType" variant="outline" theme="blue" />
    <Badge :label="intendedAudience" variant="outline" theme="gray">
      <template #prefix>
        <IconUsersGroup size="14" />
      </template>
    </Badge>
    <Badge v-if="isFirstTalk == 'Yes'" label="First Talk">
      <template #prefix>
        <IconSparkles size="14" />
      </template>
    </Badge>
  </div>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import { IconUsersGroup, IconSparkles } from '@tabler/icons-vue'

defineProps({
  sessionType: {
    type: String,
    required: true,
  },
  intendedAudience: {
    type: String,
    required: true,
  },
  isFirstTalk: {
    type: String,
    required: true,
  },
})
</script>
