<script setup>
import { createResource } from 'frappe-ui'
import { inject, onMounted, ref, computed, provide } from 'vue'
import ManageDates from '@/components/event/schedule/ManageDates.vue'
import RenderScheduleItems from '@/components/event/schedule/RenderScheduleItems.vue'
import ModifyScheduleItem from '@/components/event/schedule/ModifyScheduleItem.vue'
import ManageHallOptions from '@/components/event/schedule/ManageHallOptions.vue'
import dayjs from 'dayjs'
import { toast } from 'vue-sonner'

// Constants for default schedule times
const DEFAULT_START_TIME = '10:00'
const DEFAULT_END_TIME = '10:30'

const event = inject('event')
const schedule = computed(() => {
  let schedule_dict = {}

  event.doc?.event_schedule.forEach((schedule) => {
    if (schedule.scheduled_date in schedule_dict) {
      schedule_dict[schedule.scheduled_date].push(schedule)
    } else {
      schedule_dict[schedule.scheduled_date] = [schedule]
    }
  })

  Object.keys(schedule_dict).forEach((date) => {
    schedule_dict[date].sort((a, b) => {
      if (a.start_time == null && b.start_time == null) return 0
      if (a.start_time == null) return 1
      if (b.start_time == null) return -1
      return a.start_time.localeCompare(b.start_time)
    })
  })

  return schedule_dict
})

const linkedCfpSubmissions = computed(() => {
  return event.doc?.event_schedule.map((schedule) => schedule.linked_cfp)
})
provide('linkedCfpSubmissions', linkedCfpSubmissions)

const dates = computed({
  get() {
    return Object.keys(schedule.value)
  },
  set(newValue) {
    let newDate = newValue[newValue.length - 1]

    if (newDate) {
      addScheduleItem(newDate)
    }
  },
})
const selectedDate = ref()

const selectedScheduleItemIndex = ref()
const handleModify = (item) => {
  selectedScheduleItemIndex.value = item.idx
}

const cfpSubmissions = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      filters: {
        event: event.doc?.name,
      },
      fields: ['*'],
      limit_page_length: 99999,
    }
  },
})
onMounted(async () => {
  await cfpSubmissions.fetch()
})

provide('allCfpSubmissions', cfpSubmissions)

const addScheduleItem = (selectedDate) => {
  const dateScheduleItems = schedule.value[selectedDate] || []

  const lastItemWithEndTime = dateScheduleItems.filter((item) => item.end_time).pop()

  const newScheduleItem = {
    is_new: true,
    idx: event.doc.event_schedule.length + 1,
    title: 'Placeholder Event',
    scheduled_date: selectedDate,
  }

  if (lastItemWithEndTime) {
    newScheduleItem.start_time = lastItemWithEndTime.end_time
  } else {
    newScheduleItem.start_time = DEFAULT_START_TIME
    newScheduleItem.end_time = DEFAULT_END_TIME
  }

  event.doc.event_schedule.push(newScheduleItem)
}

const handleRemoveScheduleItem = (item) => {
  event.doc.event_schedule = event.doc.event_schedule.filter(
    (schedule) => schedule.name != item.name,
  )

  event.doc.event_schedule.forEach((schedule, index) => {
    schedule.idx = index + 1
  })

  selectedScheduleItemIndex.value = null

  handleUpdateSchedule()
  toast.info('Schedule item removed')
}

const handleUpdateSchedule = () => {
  event.doc.event_schedule.forEach((schedule) => {
    if (schedule.is_new) {
      delete schedule.is_new
    }

    if (schedule.linked_cfp && typeof schedule.linked_cfp == 'object') {
      schedule.linked_cfp = schedule.linked_cfp.value
    }
  })
  event.doc.event_schedule.forEach((schedule, index) => {
    schedule.idx = index + 1
  })

  event.setValue.submit({
    event_schedule: event.doc.event_schedule,
  })
}
</script>
<template>
  <div class="flex">
    <div class="basis-1/2 border-r min-h-svh p-6">
      <div class="prose">
        <h2 class="font-bold">Event Schedule</h2>
      </div>
      <ManageHallOptions v-if="event.doc" v-model="event.doc.hall_options" />
      <hr class="my-4" />
      <ManageDates
        v-model="dates"
        v-model:selected-date="selectedDate"
        @update:schedule="handleUpdateSchedule"
        @reset:selected-schedule="selectedScheduleItemIndex = null"
      />
      <div v-if="!selectedDate" class="flex flex-col gap-2 text-base items-center mt-12">
        <p class="text-gray-600">Select a date to add a schedule</p>
      </div>
      <div v-if="selectedDate" class="flex flex-col gap-2">
        <div class="prose">
          <h3 class="font-bold">{{ dayjs(selectedDate).format('D MMM') }}</h3>
        </div>
        <RenderScheduleItems
          v-model:schedule="schedule[selectedDate]"
          @modify-item="handleModify($event)"
        />
        <Button label="Add Schedule" icon-left="plus" @click="addScheduleItem(selectedDate)" />
      </div>
    </div>
    <Suspense>
      <div class="basis-1/2 p-6">
        <ModifyScheduleItem
          v-if="selectedScheduleItemIndex"
          v-model="event.doc.event_schedule[selectedScheduleItemIndex - 1]"
          @update:schedule="handleUpdateSchedule"
          @delete:schedule="($event) => handleRemoveScheduleItem($event)"
        />
      </div>
    </Suspense>
  </div>
</template>
