<script setup>
import SubmissionsList from './SubmissionsList.vue'
import Filter from '@/components/ui/Filter.vue'
import { IconSearch, IconDownload } from '@tabler/icons-vue'
import { createResource, FormControl, LoadingText, Select } from 'frappe-ui'
import { filterSubmissions } from '@/helpers/cfp'
import { watch, ref, computed } from 'vue'
import { useStorage } from '@vueuse/core'
import { useRoute } from 'vue-router'

const route = useRoute()

const filters = useStorage(`submission-filters:${route.params.route}`, {})
const searchTitle = ref('')

const props = defineProps({
  eventId: { type: String, required: true },
  statusFilter: { type: String, default: '' },
})

const filteredStatus = ref(props.statusFilter)

const submissions = createResource({
  url: 'fossunited.api.proposal.get_event_proposals',
  params: {
    event: props.eventId,
  },
  auto: true,
  transform(response) {
    // Handle both array and object responses
    let proposals = []

    if (Array.isArray(response)) {
      proposals = response
    } else if (response && Array.isArray(response.proposals)) {
      proposals = response.proposals
    }

    // Store metadata
    submissions.customQuestions = Array.isArray(response?.custom_questions)
      ? response.custom_questions
      : []
    submissions.eventRoute = response?.event_route || ''
    submissions.eventName = response?.event_name || 'submissions'

    // Create a deep copy to avoid reference issues
    submissions.originalData = JSON.parse(JSON.stringify(proposals))

    return proposals
  },
  onSuccess(data) {
    if (filters.value && Object.keys(filters.value).length > 0) {
      submissions.data = filterSubmissions(data, filters.value)
    }
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
  const status = filteredStatus.value

  // Ensure we have valid data
  let result = []
  if (Array.isArray(submissions.originalData)) {
    result = [...submissions.originalData]
  } else {
    return []
  }

  // Apply custom filters
  if (filters.value && Object.keys(filters.value).length > 0) {
    result = filterSubmissions(result, filters.value)
  }

  // Apply status filter
  if (status) {
    result = result.filter((item) => item.status === status)
  }

  // Apply search filter
  if (search) {
    result = result.filter((item) => {
      const { talk_title, speaker_name, speakers, _speaker } = item

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

function escapeCsv(value) {
  if (value == null) return ''
  const str = String(value)
  if (/["\n,]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

function downloadCSV() {
  const customQuestions = submissions.customQuestions || []
  const eventRoute = submissions.eventRoute || ''
  const eventName = submissions.eventName || 'submissions'
  const baseUrl = window.location.origin

  const headers = [
    'timestamp',
    'track',
    'session_title',
    'speaker',
    'review_status',
    'link',
    ...customQuestions.map((q) => q.question),
  ]

  let csv = headers.map(escapeCsv).join(',') + '\n'

  const list = submissions.data || []

  list.forEach((p) => {
    const row = [
      p.creation || '',
      p.session_type || '',
      p.talk_title || '',
      p._speaker?.[0]?.full_name || '',
      p.status || '',
      `${baseUrl}/${eventRoute}/cfp/${p.name}`,
      ...customQuestions.map((q) => {
        const value = p[`custom_question_${q.idx}`]
        return value !== undefined && value !== null ? value : ''
      }),
    ]

    csv += row.map(escapeCsv).join(',') + '\n'
  })

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `${eventName}-submissions.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

watch(
  () => props.statusFilter,
  (newVal) => {
    filteredStatus.value = newVal
  },
)

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
          <Select v-model="filteredStatus" :options="statusOptions" />
          <Filter v-if="filterFields.data" v-model="filters" :docfields="filterFields.data" />

          <button
            class="flex bg-black text-white px-3 py-2 rounded text-sm hover:bg-gray-800"
            @click="downloadCSV"
          >
            <IconDownload class="w-4 h-4 mr-1" />
            <span>CSV</span>
          </button>
        </div>
      </div>
      <SubmissionsList
        v-if="submissions.data && submissions.data.length > 0"
        v-model="submissions.data"
      />
      <div
        v-if="submissions.data?.length === 0"
        class="w-full flex justify-center items-center text-base text-gray-600"
      >
        No proposals found
      </div>
    </div>
  </Suspense>
  <LoadingText v-if="submissions.loading" class="w-5 h-5 self-center" />
</template>
