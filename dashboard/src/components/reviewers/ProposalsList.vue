<template>
  <!-- Filters -->
  <div class="flex flex-col gap-3">
    <FormControl v-model="searchTitle" label="Search" variant="outline" icon-left="search">
      <template #suffix>
        <IconSearch class="w-4" />
      </template>
    </FormControl>
    <div class="flex flex-wrap justify-between items-center gap-4">
      <Filter v-model="filters" :docfields="docfields.data" />
      <span class="text-xs text-ink-gray-5">Count: {{ cfpSubmissions.data?.length }}</span>
    </div>
  </div>

  <!-- Submission List -->
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
    <template #fallback>
      <div class="w-full h-[480px] flex items-center justify-center">
        <LoadingIndicator class="w-6 h-6" />
      </div>
    </template>
  </Suspense>
</template>
<script setup>
import ProposalListItem from './ProposalListItem.vue'
import { defineProps, watch, ref } from 'vue'
import { createResource, FormControl } from 'frappe-ui'
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

const searchTitle = ref('')
const filters = useStorage(`review-filters:${route.params.id}`, {})
const docfields = await getCfpFilterFields(route.params.id)

const cfpSubmissions = createResource({
  url: 'fossunited.api.cfp.get_cfp_submissions',
  params: {
    event: props.event,
  },
  auto: true,

  onSuccess(data) {
    if (filters.value) {
      cfpSubmissions.data = filterSubmissions(data, filters.value)
    }
  },
  transform(data) {
    cfpSubmissions.originalData = data
  },
})

watch(
  () => filters.value,
  () => {
    cfpSubmissions.data = filterSubmissions(cfpSubmissions.originalData, filters.value)
  },
  { deep: true },
)

watch(
  () => searchTitle.value,
  () => {
    const _filters = { ...filters.value, talk_title: ['like', `${searchTitle.value}`] }
    cfpSubmissions.data = filterSubmissions(cfpSubmissions.originalData, _filters)
  },
)

const handleOpenSubmission = (submission) => {
  submission._is_seen = true
  emit('open:submission', submission.name)
}
</script>
