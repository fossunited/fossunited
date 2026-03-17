<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen pb-24">
    <div class="flex flex-col md:flex-row gap-2 justify-between">
      <EventHeader
        :event="event.doc"
        :form-exists="true"
        :form="{
          data: {
            is_published: event.doc.is_published,
            doctype: 'Event',
          },
        }"
      />
      <div class="flex items-center gap-2">
        <Button
          class="w-fit"
          size="md"
          :theme="event.doc.is_published ? 'red' : 'green'"
          :icon-left="event.doc.is_published ? 'slash' : 'eye'"
          :label="event.doc.is_published ? 'Unpublish Event' : 'Publish Event'"
          @click="togglePublishEvent"
        />
        <Button
          class="w-fit"
          size="md"
          label="Update Details"
          icon-left="edit"
          @click="updateDetails()"
        ></Button>
      </div>
    </div>
    <div class="flex flex-col gap-3 my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Banner Image</div>
      <div>
        <img
          :src="getBannerImage()"
          alt="Banner Image"
          class="object-cover w-[280px] border rounded-lg aspect-[1/1]"
        />
        <div class="flex gap-2 my-2">
          <FileUploader
            :file-types="'image/*'"
            :validate-file="validateFile"
            @success="(file) => setBannerImage(file)"
          >
            <template #default="{ progress, uploading, openFileSelector }">
              <Button
                :variant="'subtle'"
                :size="'md'"
                :label="
                  uploading
                    ? `Uploading ${progress}`
                    : event.doc.banner_image
                      ? 'Change Image'
                      : 'Upload Image'
                "
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="event.doc.banner_image"
            :variant="'subtle'"
            theme="red"
            :size="'md'"
            :label="'Remove Image'"
            @click="() => setBannerImage({ file_url: '' })"
          />
        </div>
        <div class="text-sm text-ink-gray-5">
          The ideal dimensions for a banner image are: 280px x 280px (WxH) (1:1)
        </div>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Event Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_permalink"
          :type="'text'"
          size="md"
          label="Event Permalink"
          description="This text will be added to the event URL, creating a link in the format: <event-page>/<event-permalink>. Use '-' instead of spaces."
          @input="onPermalinkInput"
        />
        <div class="flex flex-col gap-2">
          <FormControl
            :disabled="true"
            :value="getEventLink()"
            type="url"
            size="md"
            label="Event Link"
            description="The event URL will appear as shown above, using the structure: <event-page>/<event-permalink>."
          >
            <template #suffix>
              <CopyToClipboardButton :value="getEventLink()" />
            </template>
          </FormControl>
          <Button
            label="See on Website"
            class="w-fit"
            icon-right="external-link"
            :link="createAbsoluteUrlFromRoute(event.doc.route)"
            :disabled="['Draft', 'Cancelled'].includes(event.doc.status)"
          />
        </div>
        <FormControl v-model="event.doc.event_name" :type="'text'" size="md" label="Event Name" />
        <FormControl
          v-model="event.doc.status"
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
          v-model="event.doc.event_type"
          :type="'select'"
          :options="eventTypeOptions.data"
          size="md"
          label="Event Type"
        />
        <FormControl
          v-model="event.doc.event_bio"
          :type="'text'"
          size="md"
          label="Short Event Bio"
          description="This bio may be used in OG images and in event cards. Typically it is a one-liner."
        />
        <FormControl
          v-model="event.doc.show_speakers"
          :type="'checkbox'"
          size="md"
          label="Show Speakers Tab"
          description="Show speakers (added in event schedule) profile linked to their proposals."
        />
        <TextEditor
          label="Event Description"
          class="col-span-2"
          :model-value="event.doc.event_description"
          @update:model-value="($event) => (event.doc.event_description = $event)"
        />
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Event Timeline</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_start_date"
          :type="'datetime-local'"
          label="Event Start Date & Time"
          size="md"
        />
        <FormControl
          v-model="event.doc.event_end_date"
          :type="'datetime-local'"
          label="Event End Date & Time"
          size="md"
        />
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Livestreaming</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.livestream_link"
          type="url"
          label="Livestream Link"
          size="md"
        />
        <FormControl
          v-model="event.doc.livestream_embed_link"
          type="url"
          label="Livestream Link (For embedding)"
          description="eg. https://youtube.com/watch?v=VIDEOID becomes https://youtube.com/embed/VIDEOID"
          size="md"
        />
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Location Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_location"
          :type="'text'"
          label="Location"
          size="md"
        />
        <FormControl
          v-model="event.doc.map_link"
          :type="'url'"
          label="Map Link"
          side="md"
          description="Prefer OpenStreetMap (OSM) links, e.g., https://osmapp.org/"
        />
      </div>
    </div>

    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Ticket Settings</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.is_paid_event"
          type="checkbox"
          size="md"
          label="Paid Event"
          description="Enable ticket purchases for this event."
        />
        <FormControl
          v-if="event.doc.is_paid_event"
          v-model="event.doc.ticket_form_description"
          type="textarea"
          size="md"
          label="Ticket Form Description"
          description="Supports markdown (bold, italic, bullet points, headings). Shown at the top of the ticket purchase page."
          class="col-span-2"
        />
      </div>
    </div>

    <FormActionBar
      :document-resource="event"
      :is-saving="event.save.loading"
      @save="updateDetails"
    />
  </div>
</template>

<script setup>
import EventHeader from '@/components/EventHeader.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import CopyToClipboardButton from '@/components/CopyToClipboardButton.vue'
import FormActionBar from '@/components/FormActionBar.vue'
import { createDocumentResource, createResource, FileUploader, FormControl } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { inject } from 'vue'

const route = useRoute()
const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})
const chapter = inject('chapter')

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(extn)) {
    toast.error('Only PNG and JPG images are allowed')
    return 'Only PNG and JPG images are allowed'
  }
}

const getBannerImage = () => {
  if (event.doc.banner_image) {
    return event.doc.banner_image
  }
  return '/assets/fossunited/images/defaults/event_banner.png'
}

const setBannerImage = (file) => {
  event.setValue.submit({
    banner_image: file.file_url,
  })
  if (file.file_url) {
    toast.success('Banner image uploaded successfully')
  } else {
    toast.info('Banner image removed successfully, will default to chapter banner if set.')
  }
}

const eventTypeOptions = createResource({
  url: 'fossunited.fossunited.utils.get_select_field_options',
  makeParams() {
    return {
      doctype_name: 'FOSS Chapter Event',
      fieldname: 'event_type',
    }
  },
  auto: true,
  transform(data) {
    return data.map((opt) => ({ label: opt, value: opt }))
  },
})

const updateDetails = () => {
  event.save
    .submit()
    .then(() => {
      toast.success('Event details updated successfully')
    })
    .catch((error) => {
      toast.error('Failed to update event details', {
        description: error.message,
      })
    })
}

const sluggify = (text) => {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const onPermalinkInput = (eventInput) => {
  const input = eventInput.target?.value ?? ''
  event.doc.event_permalink = sluggify(input)
}

const togglePublishEvent = async () => {
  try {
    if (event.doc.is_published) {
      if (!confirm('Are you sure you want to unpublish this event?')) return
    }
    await event.setValue.submit({
      is_published: !event.doc.is_published,
    })

    toast.success(event.doc.is_published ? 'Event published successfully' : 'Event unpublished')
  } catch (err) {
    toast.error('Failed to update publish status', {
      description: err.message,
    })
  }
}

const getEventLink = () => {
  const slug = sluggify(event.doc.event_permalink || '')
  const event_route = createAbsoluteUrlFromRoute(chapter.data?.route + '/' + slug)
  return event_route.replace(/(^\w+:|^)\/\//, '')
}
</script>
