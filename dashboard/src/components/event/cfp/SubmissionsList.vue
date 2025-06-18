<script setup>
import { getCfpFilterFields, filterSubmissions } from '@/helpers/cfp'
import { FormControl, ListView, createResource } from 'frappe-ui'
import { IconSearch } from '@tabler/icons-vue'
import { useStorage } from '@vueuse/core'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'
import Filter from '../../ui/Filter.vue'
import SubmissionListItem from './SubmissionListItem.vue'

const route = useRoute()

const searchTitle = ref('')
const filters = useStorage(`submission-filters:${route.params.id}`, {})
const docfields = await getCfpFilterFields(route.params.id)

defineEmits(['open:submission'])

const submissions = createResource({
  url: 'fossunited.api.cfp.get_cfp_submissions',
  params: {
    event: route.params.id,
  },
  auto: true,
  onSuccess(data) {
    if (filters.value) {
      submissions.data = filterSubmissions(data, filters.value)
    }
  },
  transform(data) {
    submissions.originalData = data
  },
})

watch(
  () => filters.value,
  () => {
    submissions.data = filterSubmissions(submissions.originalData, filters.value)
  },
  { deep: true },
)

watch(
  () => searchTitle.value,
  () => {
    const _filters = { ...filters.value, talk_title: ['like', `${searchTitle.value}`] }
    submissions.data = filterSubmissions(submissions.originalData, _filters)
  },
)
</script>

<template>
  <div class="flex gap-2 items-end">
    <FormControl v-model="searchTitle" label="Search" variant="outline" icon-left="search">
      <template #suffix>
        <IconSearch class="w-4" />
      </template>
    </FormControl>
    <Filter v-model="filters" :docfields="docfields.data" />
  </div>
  <div>
    <div v-for="submission in submissions.data" :key="submission.name">
      <SubmissionListItem
        :submission="submission"
        @open:submission="$emit('open:submission', $event)"
      />
    </div>
  </div>
</template>
