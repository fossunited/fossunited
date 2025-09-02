<script setup>
import SubmissionsList from './SubmissionsList.vue'
import Filter from '@/components/ui/Filter.vue'
import { IconSearch } from '@tabler/icons-vue'
import { createResource, FormControl, LoadingText } from 'frappe-ui'
import { filterSubmissions } from '@/helpers/cfp'
import { watch, ref } from 'vue'
import { useStorage } from '@vueuse/core'
import { useRoute } from 'vue-router'

const route = useRoute()

const filters = useStorage(`submission-filters:${route.params.route}`, {})
const searchTitle = ref('')

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
    const search = searchTitle.value.trim().toLowerCase()
    let filtered = Array.isArray(submissions.originalData) ? submissions.originalData : []

    // Apply basic field filters (status, session_type, etc.)
    if (filters.value) {
      filtered = filterSubmissions(filtered, filters.value)
    }

    // Apply search on talk title or speaker name
    if (search) {
      filtered = filtered.filter((submission) => {
        const title = submission.talk_title?.toLowerCase() ?? ''
        // Prefer pre-joined string if present; fallback to array forms.
        const speakerNameStr = submission.speaker_name?.toLowerCase() ?? ''
        let speakerMatch = false
        if (speakerNameStr) {
          speakerMatch = speakerNameStr.includes(search)
        } else {
          const speakersArr = submission.speakers ?? submission._speaker
          if (Array.isArray(speakersArr)) {
            speakerMatch = speakersArr.some((s) => s?.full_name?.toLowerCase().includes(search))
          }
        }
        return title.includes(search) || speakerMatch
      })
    }

    submissions.data = filtered
  },
)
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
        <Filter v-if="filterFields.data" v-model="filters" :docfields="filterFields.data" />
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
