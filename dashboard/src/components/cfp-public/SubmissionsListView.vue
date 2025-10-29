<script setup>
import SubmissionsList from './SubmissionsList.vue'
import Filter from '@/components/ui/Filter.vue'
import { IconSearch } from '@tabler/icons-vue'
import { createResource, FormControl, LoadingText, Select } from 'frappe-ui'
import { filterSubmissions } from '@/helpers/cfp'
import { watch, ref, computed } from 'vue'
import { useStorage } from '@vueuse/core'
import { useRoute } from 'vue-router'

const route = useRoute()

const filters = useStorage(`submission-filters:${route.params.route}`, {})
const searchTitle = ref('')
const statusFilter = ref('')

const props = defineProps({
  eventId: {
    type: String,
    required: true,
  },
})

const submissions = createResource({
  url: 'fossunited.api.proposal.get_event_proposals',
  params: {
    event: props.eventId,
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

const filterFields = createResource({
  url: 'fossunited.api.proposal.get_public_proposal_filters',
  auto: true,
  makeParams() {
    return {
      event: props.eventId,
    }
  },
})

const statusOptions = computed(() => {
  const data = filterFields.data
  if (!data || !Array.isArray(data)) return []

  const statusField = data.find((field) => field.fieldname === 'status')
  if (!statusField) return []

  const options = [
    { label: 'All', value: '' },
    ...statusField.options.split('\n').map((option) => ({
      label: option,
      value: option,
    })),
  ]

  return options
})

const filteredSubmissions = computed(() => {
  const search = searchTitle.value.trim().toLowerCase()
  const status = statusFilter.value
  let result = Array.isArray(submissions.originalData) ? [...submissions.originalData] : []

  if (filters.value) {
    result = filterSubmissions(result, filters.value)
  }

  if (status) {
    result = result.filter((item) => item.status === status)
  }

  if (search) {
    result = result.filter(({ talk_title, speaker_name, speakers, _speaker }) => {
      const titleMatch = talk_title?.toLowerCase().includes(search)
      const allNames = [
        ...(speaker_name ? [speaker_name.toLowerCase()] : []),
        ...((speakers ?? _speaker)?.map((s) => s?.full_name?.toLowerCase() ?? '') ?? []),
      ]
      return titleMatch || allNames.some((n) => n.includes(search))
    })
  }

  return result
})

watch(filteredSubmissions, (val) => {
  submissions.data = val
})
</script>
<template>
  <Suspense>
    <div class="flex flex-col gap-4 w-full mb-12">
      <div class="w-full flex justify-between items-end gap-4">
        <FormControl v-model="searchTitle" label="Search" variant="outline" icon-left="search">
          <template #suffix>
            <IconSearch class="w-4" />
          </template>
        </FormControl>
        <div class="flex items-end gap-2">
          <Select v-model="statusFilter" :options="statusOptions" />
          <Filter v-if="filterFields.data" v-model="filters" :docfields="filterFields.data" />
        </div>
      </div>
      <SubmissionsList v-model="submissions.data" />
      <div
        v-if="submissions.data?.length == 0"
        class="w-full flex justify-center items-center text-base text-gray-600"
      >
        No proposals found
      </div>
    </div>
  </Suspense>
  <LoadingText v-if="submissions.loading" class="w-5 h-5 self-center" />
</template>
