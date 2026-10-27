<script setup>
import { ref, nextTick, inject } from 'vue'
import { Button, DatePicker, Popover, Dialog } from 'frappe-ui'
import dayjs from 'dayjs'
import { toast } from 'vue-sonner'
import { IconX, IconPlus, IconAlertTriangle } from '@tabler/icons-vue'

const event = inject('event')
const emit = defineEmits(['update:schedule', 'reset:selected-schedule'])

const datePickerRef = ref(null)

const dates = defineModel({ type: Array, default: [] })
const selectedDate = defineModel('selected-date', { type: String, default: null })

const onPopoverOpen = () => {
  nextTick(() => {
    const input = datePickerRef.value?.$el.querySelector('input')
    if (input) {
      input.focus()
    }
  })
}

// Function to handle date change and close the popover
const handleDateChange = (newDate, close) => {
  dates.value = [...dates.value, newDate]
  if (close) {
    close()
  }
}

const getDateButtonVariant = (date) => {
  return selectedDate.value === date ? 'solid' : 'outline'
}

const showConfirmDialog = ref(false)
const dateToRemove = ref(null)
const handleRemoveScheduleDate = () => {
  event.doc.event_schedule = event.doc.event_schedule.filter(
    (item) => item.scheduled_date !== dateToRemove.value,
  )

  emit('update:schedule', event.doc.event_schedule)
  emit('reset:selected-schedule')

  selectedDate.value = null
  showConfirmDialog.value = false
  toast.info('Date removed')
}
</script>
<template>
  <Dialog
    v-model:open="showConfirmDialog"
    class="z-50"
    title="Confirm?"
    message="Are you sure you want to remove this date? All the schedules of this date will be removed from it."
    :icon="IconAlertTriangle"
    theme="amber"
    :actions="[
      {
        label: 'Remove Date',
        theme: 'red',
        onClick: () => {
          handleRemoveScheduleDate()
        },
      },
      {
        label: 'Cancel',
        onClick: () => (showConfirmDialog = false),
      },
    ]"
  ></Dialog>
  <div class="flex flex-wrap gap-2 items-center my-4">
    <Button
      v-for="(date, index) in dates"
      :key="index"
      :label="dayjs(date).format('D MMM YYYY')"
      :icon-right="IconX"
      :variant="getDateButtonVariant(date)"
      @click="selectedDate = date"
    >
      <template #suffix>
        <Button
          variant="ghost"
          theme="white"
          :icon="IconX"
          @click="
            () => {
              dateToRemove = date
              showConfirmDialog = true
            }
          "
        />
      </template>
    </Button>
    <Popover @open="onPopoverOpen">
      <template #trigger>
        <Button label="Add Date" variant="outline" :icon-left="IconPlus" />
      </template>
      <template #default="{ close }">
        <DatePicker
          ref="datePickerRef"
          placeholder="Select a date"
          @change="(newDate) => handleDateChange(newDate, close)"
        />
      </template>
    </Popover>
  </div>
</template>
