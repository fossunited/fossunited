<template>
  <div class="flex flex-col gap-2">
    <span class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Assign Reviewers</span>
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
import { createResource, Autocomplete, Avatar, Button } from 'frappe-ui'
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
  saveResource.submit({
    submission_name: props.submissionId,
    reviewer_users: selectedOptions.value.map((o) => o.value),
  })
}
</script>
