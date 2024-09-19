<template>
  <div class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <div v-if="chapter.doc" class="flex justify-between mt-4">
      <ChapterHeader :chapter="chapter" />
    </div>
    <div class="flex flex-col md:flex-row gap-2 justify-between mt-6 pb-2 border-b">
      <div class="text-xl font-semibold">Create Event</div>
      <Button label="Create" :variant="'solid'" size="md" @click="createEvent" />
    </div>
    <div v-if="eventTypeOptions.data">
      <div class="flex flex-col gap-3 my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Details</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
          <FormControl
            v-model="temp_event.event_name"
            :type="'text'"
            size="md"
            label="Event Name"
          />
          <FormControl
            v-model="temp_event.event_permalink"
            :type="'text'"
            size="md"
            label="Event Permalink"
            description="Only enter the event endpoint. Events will be rendered at event/<event_permalink>"
          />
          <FormControl
            v-model="temp_event.status"
            :type="'select'"
            :options="[
              {
                label: 'Draft',
                value: 'Draft',
              },
              {
                label: 'Live',
                value: 'Live',
              },
              {
                label: 'Concluded',
                value: 'Concluded',
              },
              {
                label: 'Cancelled',
                value: 'Cancelled',
              },
            ]"
            size="md"
            label="Event Status"
            description="Current status of the event."
          />
          <FormControl
            v-model="temp_event.event_type"
            :type="'select'"
            :options="eventTypeOptions.data"
            size="md"
            label="Event Type"
          />
          <TextEditor
            label="Event Description"
            class="col-span-2"
            placeholder="Write an event description"
            :model-value="temp_event.event_description"
            @update:model-value="($event) => (temp_event.event_description = $event)"
          />
        </div>
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Location</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
          <FormControl v-model="temp_event.location" :type="'text'" size="md" label="Location" />
          <FormControl v-model="temp_event.map_link" :type="'url'" label="Map Link" side="md" />
        </div>
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Timeline</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
          <FormControl
            v-model="temp_event.event_start_date"
            :type="'datetime-local'"
            size="md"
            label="Event Start Date"
          />
          <FormControl
            v-model="temp_event.event_end_date"
            :type="'datetime-local'"
            size="md"
            label="Event End Date"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import {
  usePageMeta,
  createDocumentResource,
  FormControl,
  createListResource,
  createResource,
} from 'frappe-ui'
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import ChapterHeader from '@/components/ChapterHeader.vue'
import TextEditor from '@/components/TextEditor.vue'

const route = useRoute()
const router = useRouter()

let temp_event = reactive({
  doctype: 'FOSS Chapter Event',
  chapter: route.params.id,
  event_name: '',
  event_permalink: '',
  status: '',
  event_type: '',
  event_description: '',
  location: 'TBD',
  map_link: '',
  event_start_date: '',
  event_end_date: '',
})

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
})

const eventTypeOptions = createListResource({
  doctype: 'FOSS Event Type',
  fields: ['name'],
  auto: true,
  transform(data) {
    return data.map((d) => {
      return { label: d.name, value: d.name }
    })
  },
})

const createEvent = () => {
  let event = createResource({
    url: 'frappe.client.insert',
    params: {
      doc: temp_event,
    },
  })
  event
    .submit()
    .then(() => {
      toast.success('Event Created Successfully', {
        description: 'Redirecting to the event dashboard page.',
      })
      setTimeout(() => {
        router.push(`/event/${event.data.name}`)
      }, 2000)
    })
    .catch((error) => {
      toast.error('Failed to create event', {
        description: error,
      })
    })
}

usePageMeta(() => {
  return {
    title: 'Create Event',
  }
})
</script>
