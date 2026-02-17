<template>
  <div class="flex flex-col gap-2 p-4 border border-outline-gray-2 rounded">
    <div class="flex gap-6 justify-between">
      <div class="flex flex-col gap-2 justify-between">
        <div class="flex flex-col gap-1">
          <h5 class="text-lg font-semibold text-ink-gray-9">{{ speaker.full_name }}</h5>
          <div class="flex flex-col text-sm text-ink-gray-5">
            <span>{{ speaker.designation }}</span>
            <span class="font-semibold">{{ speaker.organization }}</span>
          </div>
        </div>
        <a v-if="speaker.social_link" :href="speaker.social_link" target="_blank">
          <Badge :label="speaker.social_link" variant="outline">
            <template #prefix>
              <IconWorld class="h-4 w-4" />
            </template>
          </Badge>
        </a>
      </div>
      <img class="w-24 h-24 border rounded" :src="speaker.photo" alt="Speaker Image" />
    </div>
    <Button :label="showBio ? 'Hide Bio' : 'Show Bio'" class="w-fit" @click="showBio = !showBio" />
    <div
      v-show="showBio"
      class="prose prose-sm prose-h1:text-xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base prose-h5:text-sm prose-h1:font-semibold prose-h2:font-semibold prose-h3:font-semibold prose-h4:font-medium prose-h5:font-medium max-w-full"
      v-html="cleanedHTML(speaker.bio)"
    ></div>
  </div>
</template>
<script setup>
import { cleanedHTML } from '@/helpers/utils'
import { ref } from 'vue'
import { IconWorld } from '@tabler/icons-vue'
import { Badge } from 'frappe-ui'

const showBio = ref(false)

defineProps({
  speaker: {
    type: Object,
    required: true,
  },
})
</script>
