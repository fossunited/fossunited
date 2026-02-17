<template>
  <div class="flex flex-col gap-2 p-4 border border-outline-gray-2 rounded">
    <div class="flex gap-6 justify-between">
      <div class="flex flex-col gap-2 justify-between">
        <div class="flex flex-col gap-1">
          <h5 class="text-lg font-medium">{{ getValue('full_name') }}</h5>
          <a
            :href="
              /^https?:\/\//.test(getValue('social_link'))
                ? getValue('social_link')
                : 'https://' + getValue('social_link')
            "
            target="_blank"
          >
            <Badge
              :label="getValue('social_link')"
              variant="subtle"
              theme="gray"
              size="lg"
              class="border-outline-gray-3 border"
            >
              <template #prefix>
                <IconWorld class="h-4 w-4" />
              </template>
            </Badge>
          </a>
        </div>
        <div class="flex flex-col gap-1 text-sm font-medium">
          <span>{{ getValue('designation') }}</span>
          <span>{{ getValue('organization') }}</span>
        </div>
      </div>
      <img class="w-24 h-24 border rounded" :src="getValue('photo')" alt="Speaker Image" />
    </div>
    <div class="space-y-1 p-2">
      <label class="text-base font-medium text-ink-gray-5">Bio</label>
      <div
        class="prose prose-sm border-l pl-2 border-outline-gray-3"
        v-html="getValue('bio')"
      ></div>
    </div>
  </div>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import { IconWorld } from '@tabler/icons-vue'

const props = defineProps({
  speaker: {
    type: Object,
    required: true,
  },
})

const getValue = (fieldname) => {
  const speakerField = props.speaker.find((field) => field.fieldname === fieldname)
  return speakerField.value
}
</script>
