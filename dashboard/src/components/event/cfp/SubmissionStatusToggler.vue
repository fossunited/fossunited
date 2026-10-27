<script setup>
import { toast } from 'vue-sonner'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { Badge, Button, Dialog, createResource } from 'frappe-ui'
import { computed, inject, ref, watch } from 'vue'
import { IconCircleCheck, IconCircleX, IconHourglass } from '@tabler/icons-vue'

const submission = inject('curr_submission')
const refreshSubmissions = inject('refreshSubmissions')

// "Review Pending" is the start state only, and "Withdrawn" is set by the proposer.
// Mirrors STATUS_EMAIL_GROUPS in foss_event_cfp_submission.py.
const emailGroups = {
  Approved: 'Accepted Proposers',
  Rejected: 'Rejected Proposers',
}
// Full class strings so Tailwind's content scan picks them up.
const options = [
  {
    value: 'Screening',
    icon: IconHourglass,
    iconClass: 'text-ink-blue-7',
    selectedClass: 'has-[:checked]:bg-surface-blue-2 has-[:checked]:border-outline-blue-5',
    buttonClass:
      '!text-white !bg-surface-blue-8 hover:!bg-surface-blue-9 dark:!bg-surface-blue-6 dark:hover:!bg-surface-blue-5',
  },
  {
    value: 'Approved',
    icon: IconCircleCheck,
    iconClass: 'text-ink-green-7',
    selectedClass: 'has-[:checked]:bg-surface-green-2 has-[:checked]:border-outline-green-5',
    buttonClass:
      '!text-white !bg-surface-green-8 hover:!bg-surface-green-9 dark:!bg-surface-green-6 dark:hover:!bg-surface-green-5',
  },
  {
    value: 'Rejected',
    icon: IconCircleX,
    iconClass: 'text-ink-red-7',
    selectedClass: 'has-[:checked]:bg-surface-red-2 has-[:checked]:border-outline-red-5',
    buttonClass:
      '!text-white !bg-surface-red-7 hover:!bg-surface-red-8 dark:!bg-surface-red-6 dark:hover:!bg-surface-red-5',
  },
]
const selectedOption = computed(() => options.find((o) => o.value === newStatus.value))
const hasChange = computed(() => !!newStatus.value && newStatus.value !== currentStatus.value)

function optionHint(status) {
  if (status === currentStatus.value) return 'No change.'
  const notes = []
  if (emailGroups[currentStatus.value]) {
    notes.push(
      `All Speakers get an email & leave the ${emailGroups[currentStatus.value]} email group.`,
    )
  }
  if (emailGroups[status]) {
    notes.push(
      `All Speakers get confirmation email & join the ${emailGroups[status]} email group.`,
    )
  }
  return notes.length ? notes.join(' ') : 'No email group change.'
}

const showDialog = ref(false)
const newStatus = ref(null)

const currentStatus = computed(() => submission.data?.status)
const canChange = computed(() => currentStatus.value !== 'Withdrawn')

watch(
  () => submission.data?.name,
  () => {
    showDialog.value = false
  },
)

function openDialog() {
  newStatus.value = currentStatus.value
  showDialog.value = true
}

const changeStatus = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      name: submission.data.name,
      fieldname: 'status',
      value: newStatus.value,
    }
  },
  onSuccess() {
    showDialog.value = false
    submission.fetch()
    refreshSubmissions?.()
    toast.success(`Marked as ${newStatus.value}`)
  },
  onError(error) {
    toast.error('Failed to update status', { description: error.messages?.[0] ?? error.message })
  },
})

const dialogActions = computed(() => [
  {
    label: 'Cancel',
    onClick: ({ close }) => close(),
  },
  {
    label: hasChange.value ? `Mark as ${newStatus.value}` : 'Choose a new status',
    variant: 'solid',
    iconLeft: hasChange.value ? selectedOption.value?.icon : undefined,
    class: hasChange.value ? selectedOption.value?.buttonClass : undefined,
    disabled: !hasChange.value,
    onClick: () => changeStatus.submit(),
  },
])
</script>
<template>
  <div class="flex items-center gap-2">
    <Badge :theme="getStatusBadgeTheme(currentStatus)">{{ currentStatus }}</Badge>
    <Button v-if="canChange" variant="subtle" size="sm" aria-haspopup="dialog" @click="openDialog">
      Change
    </Button>
  </div>

  <Dialog v-model:open="showDialog" title="Change status" :actions="dialogActions">
    <!-- Dialog's `message` prop only renders when the default slot is empty -->
    <p class="mb-4 text-base font-medium text-ink-gray-9">{{ submission.data?.talk_title }}</p>
    <fieldset class="flex flex-col gap-2">
      <legend class="mb-3 text-base text-ink-gray-7 dark:text-ink-gray-8">
        Currently
        <Badge :theme="getStatusBadgeTheme(currentStatus)">{{ currentStatus }}</Badge
        >. Choose a new status.
      </legend>
      <label
        v-for="option in options"
        :key="option.value"
        class="flex cursor-pointer items-start gap-3 rounded-lg border border-outline-gray-3 p-3 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-outline-gray-5"
        :class="option.selectedClass"
      >
        <input
          v-model="newStatus"
          type="radio"
          name="submission-status"
          :value="option.value"
          :aria-describedby="`status-hint-${option.value}`"
          class="mt-1 focus:outline-none focus:ring-0 focus:ring-offset-0"
        />
        <span class="flex flex-col gap-1">
          <span class="flex items-center gap-2 text-base font-medium text-ink-gray-9">
            <component
              :is="option.icon"
              class="size-4 shrink-0"
              :class="option.iconClass"
              aria-hidden="true"
            />
            {{ option.value }}
            <span
              v-if="option.value === currentStatus"
              class="text-sm font-normal text-ink-gray-7 dark:text-ink-gray-8"
            >
              (current)
            </span>
          </span>
          <span
            :id="`status-hint-${option.value}`"
            class="text-sm text-ink-gray-7 dark:text-ink-gray-8"
          >
            {{ optionHint(option.value) }}
          </span>
        </span>
      </label>
    </fieldset>
  </Dialog>
</template>
