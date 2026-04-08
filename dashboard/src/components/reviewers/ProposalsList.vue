<template>
  <!-- Filters -->
  <div class="flex flex-col gap-3">
    <FormControl v-model="searchTitle" label="Search" variant="outline" icon-left="search">
      <template #suffix>
        <IconSearch class="w-4" />
      </template>
    </FormControl>
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <Filter v-model="filters" :docfields="docfields.data" />
          <Switch v-model="showNotReviewed" label="Hide reviewed (By Me)" />
      </div>
      <span class="text-xs text-ink-gray-5">Count: {{ cfpSubmissions.data?.length }}</span>
    </div>
  </div>

  <!-- Submission List -->
  <div v-if="cfpSubmissions.loading" class="flex flex-col items-center gap-2">
    <LoadingIndicator class="w-5 h-5" />
  </div>
  <Suspense>
    <template #default>
      <div v-if="cfpSubmissions.data" class="flex flex-col">
        <ProposalListItem
          v-for="submission in cfpSubmissions.data"
          :key="submission.name"
          :submission="submission"
          tabindex="0"
          @click="handleOpenSubmission(submission)"
        />
        <div v-if="cfpSubmissions.data.length === 0">
          <span class="text-sm text-ink-gray-5"> No submissions found.</span>
        </div>
      </div>
    </template>
  </Suspense>
</template>
<script setup>
import ProposalListItem from './ProposalListItem.vue'
import { watch, ref } from 'vue'
import { createResource, FormControl, LoadingIndicator, Switch } from 'frappe-ui'
import Filter from '../ui/Filter.vue'
import { getCfpFilterFields, filterSubmissions } from '@/helpers/cfp'
import { useRoute } from 'vue-router'
import { useStorage } from '@vueuse/core'
import { IconSearch } from '@tabler/icons-vue'

const route = useRoute()

const props = defineProps({
  event: {
    type: String,
    required: true,
  },
  justReviewed: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['open:submission'])

const showNotReviewed = ref(true)
const searchTitle = ref('')
const filters = useStorage(`review-filters:${route.params.id}`, {})
const docfields = await getCfpFilterFields(route.params.id)

const cfpSubmissions = createResource({
  url: 'fossunited.api.cfp.get_cfp_submissions',
  params: {
    event: props.event,
  },
  auto: true,
  transform(data) {
    // Exclude withdrawn proposals from the list
    const withoutWithdrawn = data.filter((s) => s.status !== 'Withdrawn')
    cfpSubmissions.originalData = withoutWithdrawn
    return withoutWithdrawn
  },
  onSuccess() {
    applyFilters()
  },
})

function applyFilters() {
  if (!cfpSubmissions.originalData) return
  const _filters = {
    ...filters.value,
    ...(searchTitle.value ? { talk_title: ['like', searchTitle.value] } : {}),
    ...(showNotReviewed.value && !filters.value?._is_reviewed
      ? { _is_reviewed: ['=', 'No'] }
      : {}),
  }
  cfpSubmissions.data = filterSubmissions(cfpSubmissions.originalData, _filters)
}

watch(
  [() => filters.value, () => searchTitle.value, () => showNotReviewed.value],
  () => applyFilters(),
  { deep: true },
)

const handleOpenSubmission = (submission) => {
  submission._is_seen = true
  emit('open:submission', submission.name)
}
</script>
