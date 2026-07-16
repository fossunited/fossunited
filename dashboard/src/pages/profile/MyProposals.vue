<template>
  <div class="space-y-3">
    <div class="prose p-4 pb-0">
      <h2 class="mb-1">My Proposals</h2>
      <p class="text-sm mb-4">Overview of all the talks you have ever proposed</p>
    </div>
    <div v-if="proposals.data?.length" class="px-4">
      <FormControl
        v-model="search"
        type="text"
        size="sm"
        variant="subtle"
        placeholder="Search by title, event or status"
      >
        <template #prefix>
          <IconSearch class="w-4 h-4 text-ink-gray-5" />
        </template>
      </FormControl>
    </div>
    <div v-if="proposals.loading" class="px-4">
      <LoadingText />
    </div>
    <div v-if="proposals.data" class="px-4">
      <p v-if="!proposals.data.length" class="text-sm text-ink-gray-5">No submissions yet.</p>
      <p v-else-if="!filteredProposals.length" class="text-sm text-ink-gray-5">
        No proposals match "{{ search }}".
      </p>
      <SubmissionListItem
        v-for="(proposal, key) in filteredProposals"
        :key="key"
        :proposal="proposal"
      />
    </div>
  </div>
</template>
<script setup>
import { createResource, FormControl } from 'frappe-ui'
import LoadingText from 'frappe-ui/src/components/LoadingText.vue'
import { IconSearch } from '@tabler/icons-vue'
import { computed, inject, ref } from 'vue'
import SubmissionListItem from '@/components/profile/SubmissionListItem.vue'

const session = inject('$session')
const search = ref('')

const proposals = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      fields: [
        'name',
        'status',
        'event_name',
        'session_type',
        'talk_title',
        'route',
        'creation',
        'modified',
      ],
      orderBy: 'creation',
      limit_page_length: 999,
      or_filters: { email: session.user, submitted_by: session.user },
    }
  },
  auto: true,
  loading: true,
})

const filteredProposals = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return proposals.data ?? []
  return (proposals.data ?? []).filter((p) =>
    [p.talk_title, p.event_name, p.status].some((f) => f?.toLowerCase().includes(q)),
  )
})
</script>
