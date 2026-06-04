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
      <div class="flex items-center gap-2">
        <FormControl
          v-model="sortBy"
          type="select"
          :options="SORT_OPTIONS"
          size="sm"
          class="text-xs"
        />
        <span class="text-xs text-ink-gray-5 whitespace-nowrap"
          >Count: {{ cfpSubmissions.data?.length }}</span
        >
      </div>
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
      :sort-by="sortBy"
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
import { toast } from 'vue-sonner'

// Module-level: resets on page refresh, survives component remounts within same load.
const _assignedToggleCache = new Map()
// Tracks events where the "all assigned reviewed" auto-untoggle already fired this page load.
// Prevents re-firing when user manually re-enables the toggle.
const _autoUntoggleFiredCache = new Set()

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
const sortBy = ref('creation_desc')

// Restore from cache if user already toggled this session; default false until smart default runs.
const showAssignedOnly = ref(_assignedToggleCache.get(props.event) ?? false)

watch(showAssignedOnly, (val) => {
  _assignedToggleCache.set(props.event, val)
})

const filters = useStorage(storageKey, {})
const docfields = await getCfpFilterFields(route.params.id)

const SORT_OPTIONS = computed(() => {
  const options = [
    { label: 'Newest first', value: 'creation_desc' },
    { label: 'Oldest first', value: 'creation_asc' },
    { label: 'Review count ↓', value: 'review_count_desc' },
    { label: 'Title A–Z', value: 'title_asc' },
  ]
  if (!props.reviewerMode) {
    options.splice(3, 0, { label: 'Assigned count ↓', value: 'assigned_count_desc' })
  }
  return options
})

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
  onSuccess(data) {
    if (props.reviewerMode && !_assignedToggleCache.has(props.event)) {
      const hasAssigned = data.some((s) => s._is_assigned === 'Yes')
      showAssignedOnly.value = hasAssigned
      if (!hasAssigned) {
        toast('No proposals assigned to you - showing all.')
      }
    }
    applyFilters()
  },
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

  const baseFieldFilters = {
    ...filters.value,
    ...(props.reviewerMode && showNotReviewed.value && !filters.value?._is_reviewed
      ? { _is_reviewed: ['=', 'No'] }
      : {}),
  }

  if (Object.keys(baseFieldFilters).length > 0) {
    data = filterSubmissions(data, baseFieldFilters)
  }

  // Check assigned filter separately so we can detect "all assigned are reviewed".
  if (props.reviewerMode && showAssignedOnly.value) {
    const assignedData = filterSubmissions(data, { _is_assigned: ['=', 'Yes'] })
    if (
      assignedData.length === 0 &&
      data.length > 0 &&
      !_autoUntoggleFiredCache.has(props.event)
    ) {
      // Reviewer finished all assigned proposals — auto-untoggle once per page load.
      // After this fires, user can manually re-enable without it fighting back.
      _autoUntoggleFiredCache.add(props.event)
      showAssignedOnly.value = false
      toast('All your assigned proposals are reviewed - showing rest of them.')
      return // watch re-runs applyFilters with showAssignedOnly=false
    }
    data = assignedData
  }

  data = [...data].sort((a, b) => {
    switch (sortBy.value) {
      case 'creation_asc':
        return new Date(a.creation) - new Date(b.creation)
      case 'review_count_desc':
        return (b._review_count ?? 0) - (a._review_count ?? 0)
      case 'assigned_count_desc':
        return (b._assigned_users?.length ?? 0) - (a._assigned_users?.length ?? 0)
      case 'title_asc':
        return (a.talk_title || '').localeCompare(b.talk_title || '')
      default:
        return new Date(b.creation) - new Date(a.creation)
    }
  })

  cfpSubmissions.data = data
}

watch([filters, searchQuery, selectedStatus, sortBy], applyFilters, { deep: true })
watch([showNotReviewed, showAssignedOnly], applyFilters)

function patchAssignedUsers(name, newUsers) {
  const patcher = (item) => {
    if (item.name !== name) return
    const verdictMap = Object.fromEntries(
      (item._assigned_users ?? []).map((u) => [u.user, u._review_verdict]),
    )
    item._assigned_users = newUsers.map((u) => ({
      ...u,
      _review_verdict: verdictMap[u.user] ?? null,
    }))
    item._is_assigned = newUsers.length > 0 ? 'Yes' : 'No'
  }
  cfpSubmissions.originalData?.forEach(patcher)
  applyFilters()
}

function handleOpenSubmission(submission) {
  submission._is_seen = true
  emit('open:submission', submission.name)
}

defineExpose({
  reloadSubmissions: () => cfpSubmissions.reload(),
  patchAssignedUsers,
})
</script>
