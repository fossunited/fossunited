<script setup>
import { toast } from 'vue-sonner'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { Badge, Dialog, createResource } from 'frappe-ui'
import { inject, ref, watch } from 'vue'
import {
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectItemText,
  SelectLabel,
  SelectPortal,
  SelectRoot,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from 'radix-vue'
import { IconChevronDown } from '@tabler/icons-vue'

const submission = inject('curr_submission')

const newStatus = ref(submission.data.status)

const options = ['Approved', 'Rejected', 'Screening']

const showDialog = ref(false)

const emit = defineEmits(['status-change'])

watch(
  () => newStatus.value,
  () => {
    showDialog.value = true
  },
)

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

  onSuccess(data) {
    emit('status-change', newStatus.value)
    showDialog.value = false
    submission.fetch()
    toast.success('Status updated successfully')
  },
  onError(error) {
    toast.error('Failed to update status', error.message)
  },
})
</script>
<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Confirm',
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'Confirm',
          variant: 'solid',
          onClick: () => {
            changeStatus.fetch()
          },
          loading: changeStatus.loading,
        },
        {
          label: 'Cancel',
          onClick: () => (showDialog = false),
        },
      ],
    }"
  >
    <template #body-content>
      <div>
        <p class="text-base leading-6">
          Are you sure you want to change the status of this submission from
          <Badge :theme="getStatusBadgeTheme(submission.data.status)">
            {{ submission.data.status }}
          </Badge>
          to
          <Badge :theme="getStatusBadgeTheme(newStatus)">{{ newStatus }}</Badge> ?
        </p>
      </div>
    </template>
  </Dialog>
  <br />
  <SelectRoot v-model="newStatus">
    <SelectTrigger
      class="inline-flex min-w-32 items-center rounded text-sm leading-none h-8 gap-2 bg-surface-white"
      aria-label="Customise options"
    >
      <SelectValue>
        <Badge :theme="getStatusBadgeTheme(submission.data.status)">
          {{ submission.data.status }}
        </Badge>
      </SelectValue>
      <IconChevronDown class="w-4 h-4 text-ink-gray-5" />
    </SelectTrigger>

    <SelectPortal>
      <SelectContent class="bg-surface-white border shadow-xl rounded p-4 px-2 z-[100]">
        <SelectViewport>
          <SelectGroup>
            <SelectLabel class="text-ink-gray-6 text-sm">Options</SelectLabel>
            <SelectSeparator class="h-px bg-gray-400 my-2" />
            <div class="flex flex-col gap-2">
              <SelectItem
                v-for="option in options"
                :key="option"
                :value="option"
                class="flex items-center gap-2 p-1 text-sm cursor-pointer hover:bg-surface-gray-2 rounded"
              >
                <SelectItemText>
                  <Badge :theme="getStatusBadgeTheme(option)">{{ option }}</Badge>
                </SelectItemText>
              </SelectItem>
            </div>
          </SelectGroup>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
