<template>
  <div v-if="event.data" class="w-full">
    <EventHeader :event="event.data" class="p-4 md:p-8" />
    <hr />
    <div class="p-4 md:px-8 md:py-6">
      <div class="prose">
        <h2 class="mb-1">Attendee Check-Ins</h2>
        <p class="text-sm">Check in attendees as they arrive at the event.</p>
      </div>
      <div class="flex flex-col my-4 justify-center">
        <div class="flex flex-col gap-2 mb-4 mt-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 items-center">
            <FormControl
              v-model="filters.name"
              label="Ticket ID"
              placeholder="Search by Ticket ID"
              @input="attendees.fetch()"
            />
            <FormControl
              v-model="filters.full_name"
              label="Name"
              type="text"
              placeholder="Search by Name"
              @input="attendees.fetch()"
            />
            <FormControl
              v-model="filters.email"
              label="Email"
              type="text"
              placeholder="Search by Email"
              @input="attendees.fetch()"
            />
          </div>
          <Button
            class="w-fit"
            label="Search"
            variant="solid"
            @click="attendees.fetch()"
            :loading="attendees.loading"
            loadingText="Searching..."
          />
        </div>
        <div v-if="attendees.data">
          <ListView
            :columns="[
              { label: 'Ticket ID', key: 'name', width: 1 / 5 },
              { label: 'Name', key: 'full_name', width: 1 / 5 },
              { label: 'Check-in Status', key: 'checkin_status', width: 2 / 5 },
              { label: 'Actions', key: 'action', width: 1 / 5 },
            ]"
            :rows="attendees.data"
            :options="{
              selectable: false,
              showTooltip: false,
              resizeColumn: true,
              emptyState: {
                title: 'No attendees found',
              },
            }"
            row-key="name"
          >
            <template #cell="{ item, row, column }">
              <template v-if="column.key === 'action'">
                <Button
                  v-if="!isCheckedInToday(row)"
                  class="w-fit"
                  label="Check-in"
                  variant="solid"
                  @click="() => {
                    selectedAttendee = row
                    checkinAttendee.fetch()
                  }"
                  :loading="checkinAttendee.loading && selectedAttendee.name === row.name"
                  loadingText="Checking in..."
                />
                <Button
                  v-else
                  class="w-fit"
                  label="Undo"
                  @click="() => {
                    selectedAttendee = row
                    undoAttendeeCheckin.fetch()
                  }"
                />
              </template>
              <template v-else-if="column.key ==='name'">
                <span class="font-mono text-sm font-semibold text-gray-800">{{ item }}</span>
              </template>
              <template v-else-if="column.key === 'checkin_status'">
                <div class="flex items-center overflow-hidden overflow-x-visible flex-wrap">
                  <span
                    v-for="data in row.checkin_data"
                    class="flex items-center p-1 rounded-sm"
                  >
                    <Tooltip
                      arrow-class="fill-black"
                      :placement="'top'"
                      :hoverDelay="0.5"
                    >
                      <template #body>
                        <span class="text-xs bg-gray-900 text-white px-2 py-1 rounded-full">
                          {{ getFormattedDateTime(data.check_in_time) }}
                        </span>
                      </template>
                      <Badge :theme="getRelativeTime(data.check_in_time) == 'Today' ? 'green' : 'gray'" class="flex gap-1 items-center">
                        <DoubleChecksIcon class="w-4 h-4" />
                        <span>{{ getRelativeTime(data.check_in_time) }}</span>
                      </Badge>
                    </Tooltip>
                  </span>
                </div>
              </template>
              <template v-else class="text-base">
                {{ item }}
              </template>
            </template>
          </ListView>
        </div>
        <div v-else>
          <LoadingText />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import DoubleChecksIcon from '@/components/icons/DoubleChecks.vue'
import EventHeader from '@/components/EventHeader.vue'
import {
  FormControl,
  createResource,
  usePageMeta,
  LoadingText,
  ListView,
  Badge,
  Tooltip,
} from 'frappe-ui'
import { useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import isToday from 'dayjs/plugin/isToday'
import isYesterday from 'dayjs/plugin/isYesterday'

dayjs.extend(relativeTime)
dayjs.extend(isToday)
dayjs.extend(isYesterday)

const session = inject('$session')

const route = useRoute()

const event = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fields: ['*'],
    }
  },
  auto: true,
})

usePageMeta(() => {
  return {
    title: `Check-ins | ${event.data?.event_name}`,
  }
})

const filters = reactive({
  name: '',
  full_name: '',
  email: '',
})

const attendees = createResource({
  url: 'fossunited.api.checkins.get_attendee_with_checkin_data',
  makeParams() {
    return {
      event_id: route.params.id,
      user: session.user,
      filters: filters,
    }
  },
  auto: true,
  debounce: 500,
})

const selectedAttendee = ref(null)

const checkinAttendee = createResource({
  url: 'fossunited.api.checkins.checkin_attendee',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: selectedAttendee.value,
      user: session.user,
    }
  },
  onSuccess() {
    makeChangesToAttendeeDict(selectedAttendee.value)
    selectedAttendee.value = null
  },
})

const undoAttendeeCheckin = createResource({
  url: 'fossunited.api.checkins.undo_attendee_checkin',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: selectedAttendee.value,
      user: session.user,
    }
  },
  onSuccess() {
    const index = attendees.data.findIndex((data) => data.name === selectedAttendee.value.name)
    attendees.data[index].checkin_data.shift()
    selectedAttendee.value = null
  },
})

const makeChangesToAttendeeDict = (attendee) => {
  const index = attendees.data.findIndex((data) => data.name === attendee.name)
  attendees.data[index].checkin_data.unshift({
    check_in_time: new Date(),
  })
}

const isCheckedInToday = (attendee) => {
  return attendee.checkin_data.some((data) => dayjs(data.check_in_time).isToday())
}

const getFormattedDateTime = (datetime) => {
  return dayjs(datetime).format('DD MMM, hh:mm A')
}

const getRelativeTime = (datetime) => {
  const date = dayjs(datetime)
  if (date.isToday()) {
    return 'Today'
  } else if (date.isYesterday()) {
    return 'Yesterday'
  } else {
    return date.fromNow()
  }
}
</script>
