<template>
  <div v-if="submission.data" class="w-full md:p-6 flex flex-col gap-4">
    <div class="flex flex-col gap-2">
      <ProposalBadgeGroup
        :session-type="submission.data.session_type"
        :intended-audience="submission.data.intended_audience"
        :is-first-talk="submission.data.is_first_talk"
      />
      <div class="prose-sm">
        <h2 class="font-semibold">{{ submission.data.talk_title }}</h2>
      </div>
      <div class="flex items-center gap-2">
        <Badge
          :label="submission.data.status"
          :theme="getStatusBadgeTheme(submission.data.status)"
        />
        <Badge v-if="submission.data.hasReviewed" label="Reviewed" theme="blue" />
        <span class="text-sm text-ink-gray-5">
          Submitted {{ dayjs(submission.data.creation).fromNow() }}
        </span>
      </div>
      <a
        class="flex gap-1 items-center text-sm text-ink-gray-5 hover:cursor-pointer hover:text-ink-gray-8 transition-colors"
        :href="createAbsoluteUrlFromRoute(submission.data.route)"
        target="_blank"
      >
        <span> View Public Page </span>
        <IconArrowUpRight class="w-4 h-4" />
      </a>
    </div>
    <TabButtons v-if="tabs.length > 1" v-model="activeTab" class="w-fit" :buttons="tabs" />
    <div v-if="activeTab === 0" class="flex flex-col gap-4">
      <ProseContainer label="Session Description" :value="submission.data.talk_description" />
      <ProseContainer label="Key Takeaways" :value="submission.data.key_takeaways" />
      <RenderReferences :references="submission.data.references" />
      <RenderSessionCategories :categories="submission.data.session_categories" />
      <div v-if="submission.data.talk_license" class="flex flex-col gap-1">
        <span class="text-xs font-medium text-ink-gray-5 uppercase">License</span>
        <div class="flex items-center gap-1.5 text-sm text-ink-gray-7">
          <IconScale class="w-4 h-4 text-ink-gray-4 flex-shrink-0" />
          <span>{{ submission.data.talk_license }}</span>
        </div>
      </div>
    </div>
    <div
      v-else-if="activeTab === 1 && !hasAnonymousSpeaker.data.anonymise_proposals"
      class="flex flex-col gap-2"
    >
      <ProposalSpeakers :speakers="submission.data.speakers" />
    </div>
    <div v-else-if="activeTab === 2" class="flex flex-col gap-2">
      <ReviewSection :reviews="submission.data.reviews" @review:submitted="emit('review:submitted')" />
    </div>
  </div>
  <div v-else class="w-full h-[480px] flex items-center justify-center">
    <LoadingIndicator class="w-6 h-6" />
  </div>
</template>
<script setup>
import { createResource, LoadingIndicator, Badge, TabButtons } from 'frappe-ui'
import { provide, ref, watch, inject } from 'vue'
import { useRoute } from 'vue-router'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { IconArrowUpRight, IconScale } from '@tabler/icons-vue'
import ProposalSpeakers from './ProposalSpeakers.vue'
import ProseContainer from '@/components/ui/ProseContainer.vue'
import ProposalBadgeGroup from './ProposalBadgeGroup.vue'
import RenderReferences from '@/components/cfp-public/RenderReferences.vue'
import RenderSessionCategories from '@/components/cfp-public/RenderSessionCategories.vue'
import ReviewSection from './ReviewSection.vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const route = useRoute()

const emit = defineEmits(['toggle-reviewed', 'review:submitted'])

const submissionId = defineModel('submissionId', {
  type: String,
  required: true,
})

const tabs = ref([
  {
    label: 'Overview',
    value: 0,
  },
  {
    label: 'Reviews',
    value: 2,
  },
])
const activeTab = ref(0)

const hasAnonymousSpeaker = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP',
      fieldname: 'anonymise_proposals',
      filters: { event: route.params.id },
    }
  },
  onSuccess(data) {
    if (!data.anonymise_proposals) {
      tabs.value.splice(1, 0, {
        label: 'Speaker Information',
        value: 1,
      })
    }
  },
  auto: true,
})

const session = inject('$session')

const submission = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      fields: ['*'],
      filters: { name: submissionId.value },
    }
  },
  transform(data) {
    // Ensure session_categories is always an array
    data.session_categories = (data.session_categories ?? '').split('\n').filter(Boolean)

    // Ensure reviews is always an array
    data.reviews = data.reviews ?? []

    data.hasReviewed = data.reviews.some((review) => review.owner === session.user)

    return data
  },
})

watch(
  () => submissionId.value,
  (newId) => {
    if (newId) {
      submission.fetch()
      provide('submission', submission.data)
    }
  },
  { immediate: true },
)

provide('submission', submission)
</script>
