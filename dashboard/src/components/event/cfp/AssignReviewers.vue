<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center gap-1">
      <span class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Assign Reviewers</span>
      <Tooltip text="Assigning a reviewer sends them an email notification. Use only to notify reviewers to review this proposal." placement="right">
        <a
          href="https://docs.fossunited.org/event-cfp#assign-reviewers-to-a-proposal"
          target="_blank"
          rel="noopener noreferrer"
          class="text-ink-gray-4 hover:text-ink-gray-6 leading-none"
        >
          <IconHelpCircle class="w-3.5 h-3.5" />
        </a>
      </Tooltip>
    </div>
    <div class="flex gap-2 items-start">
      <Autocomplete
        v-model="selectedOptions"
        :options="reviewerOptions"
        :multiple="true"
        placeholder="Select reviewers..."
        class="flex-1"
      >
        <template #item-prefix="{ option }">
          <Avatar :image="option.user_image" :label="option.label" size="xs" class="mr-1.5" />
        </template>
      </Autocomplete>
      <Button
        label="Save"
        size="sm"
        variant="solid"
        :loading="saveResource.loading"
        @click="saveAssignments"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { createResource, Autocomplete, Avatar, Button, Tooltip } from 'frappe-ui'
import { IconHelpCircle } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'

const props = defineProps({
  submissionId: { type: String, required: true },
  eventId: { type: String, required: true },
})

const reviewers = createResource({
  url: 'fossunited.api.cfp.get_cfp_reviewers',
  params: { event_id: props.eventId },
  auto: true,
})

const currentAssignments = createResource({
  url: 'fossunited.api.cfp.get_submission_reviewer_assignments',
  makeParams() {
    return { submission_name: props.submissionId }
  },
  auto: true,
})

const selectedOptions = ref([])
let initializing = false

watch(
  [() => currentAssignments.data, () => reviewers.data],
  ([assignments, reviewerList]) => {
    if (!assignments || !reviewerList) return
    initializing = true
    selectedOptions.value = reviewerList
      .filter((r) => assignments.includes(r.user))
      .map((r) => ({ label: r.full_name, value: r.user, user_image: r.user_image }))
    nextTick(() => {
      initializing = false
    })
  },
)

watch(
  () => props.submissionId,
  () => {
    selectedOptions.value = []
    currentAssignments.reload()
  },
)

const reviewerOptions = computed(
  () =>
    (reviewers.data || []).map((r) => ({
      label: r.full_name,
      value: r.user,
      user_image: r.user_image,
    })),
)

const saveResource = createResource({
  url: 'fossunited.api.cfp.set_submission_reviewers',
  onSuccess() {
    toast.success('Reviewers updated')
  },
  onError(err) {
    toast.error('Failed to update reviewers', { description: err.message })
  },
})

function saveAssignments() {
  const newSet = new Set(selectedOptions.value.map((o) => o.value))
  const removed = (currentAssignments.data || []).filter((u) => !newSet.has(u))

  if (removed.length > 0) {
    const names = removed
      .map((u) => reviewers.data?.find((r) => r.user === u)?.full_name || u)
      .join(', ')
    const ok = window.confirm(
      `Remove ${removed.length} reviewer${removed.length > 1 ? 's' : ''}: ${names}?\n\nThey will no longer see this proposal as assigned to them.`,
    )
    if (!ok) return
  }

  saveResource.submit({
    submission_name: props.submissionId,
    reviewer_users: selectedOptions.value.map((o) => o.value),
  })
}
</script>
