<template>
  <div class="flex flex-col gap-3">
    <!-- Search -->
    <FormControl v-model="searchQuery" label="Search" variant="outline">
      <template #suffix>
        <IconSearch class="w-4" />
      </template>
    </FormControl>

    <!-- Status pills -->
    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="s in statusOptions"
        :key="s.value"
        class="px-2.5 py-1 rounded-full text-xs font-medium transition-colors"
        :class="
          selectedStatus === s.value
            ? s.activeClass
            : 'bg-surface-gray-2 text-ink-gray-6 hover:bg-surface-gray-3'
        "
        @click="selectedStatus = selectedStatus === s.value && s.value !== '' ? '' : s.value"
      >
        {{ s.label }}
      </button>
    </div>

    <!-- Filter row -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <Filter v-model="filters" :docfields="docfields.data" />
        <Tooltip text="Only show submissions you haven't reviewed yet">
          <Switch v-if="reviewerMode" v-model="showNotReviewed" label="Hide reviewed (By Me)" />
        </Tooltip>
        <Tooltip text="Only show submissions assigned to you">
          <Switch v-if="reviewerMode" v-model="showAssignedOnly" label="Assigned to me" />
        </Tooltip>
      </div>
      <span class="text-xs text-ink-gray-5">Count: {{ cfpSubmissions.data?.length }}</span>
    </div>
  </div>

  <!-- List -->
  <div v-if="cfpSubmissions.loading" class="flex items-center justify-center py-4">
    <LoadingIndicator class="w-5 h-5" />
  </div>
  <div v-else-if="cfpSubmissions.data" class="flex flex-col">
    <SubmissionListItem
      v-for="submission in cfpSubmissions.data"
      :key="submission.name"
      :submission="submission"
      tabindex="0"
      @open:submission="handleOpenSubmission($event)"
    />
    <div v-if="cfpSubmissions.data.length === 0" class="py-4">
      <span class="text-sm text-ink-gray-5">No submissions found.</span>
    </div>
  </div>
</template>

<script setup>
import SubmissionListItem from './SubmissionListItem.vue'
import Filter from '@/components/ui/Filter.vue'
import { getCfpFilterFields, filterSubmissions } from '@/helpers/cfp'
import { useRoute } from 'vue-router'
import { useStorage } from '@vueuse/core'
import { ref, watch, computed } from 'vue'
import { createResource, FormControl, LoadingIndicator, Switch, Tooltip } from 'frappe-ui'
import { IconSearch } from '@tabler/icons-vue'

const props = defineProps({
  event: {
    type: String,
    required: true,
  },
  reviewerMode: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['open:submission'])

const route = useRoute()
const storageKey = props.reviewerMode
  ? `review-filters:${props.event}`
  : `submission-filters:${props.event}`

const searchQuery = ref('')
const selectedStatus = ref('')
const showNotReviewed = ref(true)
const showAssignedOnly = ref(true)
const filters = useStorage(storageKey, {})
const docfields = await getCfpFilterFields(route.params.id)

const STATUS_OPTIONS = [
  { value: '', label: 'All', activeClass: 'bg-surface-gray-7 text-ink-white' },
  {
    value: 'Review Pending',
    label: 'Review Pending',
    activeClass: 'bg-orange-100 text-orange-700',
  },
  { value: 'Approved', label: 'Approved', activeClass: 'bg-green-100 text-green-700' },
  { value: 'Rejected', label: 'Rejected', activeClass: 'bg-red-100 text-red-700' },
]

const statusOptions = computed(() => {
  if (props.reviewerMode) return STATUS_OPTIONS
  return [
    ...STATUS_OPTIONS,
    { value: 'Withdrawn', label: 'Withdrawn', activeClass: 'bg-surface-gray-3 text-ink-gray-6' },
  ]
})

const cfpSubmissions = createResource({
  url: 'fossunited.api.cfp.get_cfp_submissions',
  params: { event: props.event },
  auto: true,
  transform(data) {
    const filtered = props.reviewerMode ? data.filter((s) => s.status !== 'Withdrawn') : data
    cfpSubmissions.originalData = filtered
    return filtered
  },
  onSuccess() {
    applyFilters()
  },
})

defineExpose({
  reloadSubmissions: () => cfpSubmissions.reload(),
})

function applyFilters() {
  if (!cfpSubmissions.originalData) return

  const search = searchQuery.value.trim().toLowerCase()
  let data = search
    ? cfpSubmissions.originalData.filter(
        (s) =>
          s.talk_title?.toLowerCase().includes(search) ||
          s.speaker_name?.toLowerCase().includes(search),
      )
    : cfpSubmissions.originalData

  if (selectedStatus.value) {
    data = data.filter((s) => s.status === selectedStatus.value)
  }

  const fieldFilters = {
    ...filters.value,
    ...(props.reviewerMode && showNotReviewed.value && !filters.value?._is_reviewed
      ? { _is_reviewed: ['=', 'No'] }
      : {}),
    ...(props.reviewerMode && showAssignedOnly.value ? { _is_assigned: ['=', 'Yes'] } : {}),
  }

  if (Object.keys(fieldFilters).length > 0) {
    data = filterSubmissions(data, fieldFilters)
  }

  cfpSubmissions.data = data
}

watch([filters, searchQuery, selectedStatus], applyFilters, { deep: true })
watch([showNotReviewed, showAssignedOnly], applyFilters)

function handleOpenSubmission(submission) {
  submission._is_seen = true
  emit('open:submission', submission.name)
}
</script>
