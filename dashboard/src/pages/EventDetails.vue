<template>
<div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <Toast
        v-if="showToast"
        class="z-10 absolute"
        :class="toastTitle == 'Success' ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'"
        :icon="toastTitle == 'Success' ? 'check-circle' : 'x'"
        icon-classes="stroke-2"
        :title="toastTitle"
        :text="toastMessage"
        position="bottom-right"
    />
    <div class="flex flex-col md:flex-row gap-2 justify-between">
        <EventHeader
            :event="event"
        />
        <Button
            class="w-fit"
            size="md"
            label="Update Details"
            icon-left="edit"
            @click="updateDetails()"
        ></Button>
    </div>
    <div class="flex flex-col gap-3 my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Banner Image</div>
        <div>
            <img :src="getBannerImage()" alt="Banner Image" class="object-cover w-full border rounded-lg aspect-[4.96/1]">
            <div class="flex gap-2 my-2">
                <FileUploader
                    :fileTypes="'image/*'"
                    :validateFile="validateFile"
                    @success="(file) => setBannerImage(file)"
                >
                    <template v-slot="{ file, progress, error, uploading, openFileSelector }">
                        <Button
                            :variant="'subtle'"
                            :size="'md'"
                            :label="uploading ? `Uploading ${progress}` : event.doc.banner_image ? 'Change Image' : 'Upload Image'"
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
            <div class="text-sm text-gray-600">The ideal dimensions for a banner image are: 1240 x 300 (WxH)</div>
        </div>
    </div>
    <div class="flex flex-col my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Event Details</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
                :type="'text'"
                size="md"
                v-model="event.doc.event_name"
                label="Event Name"
            />
            <FormControl
                :type="'text'"
                size="md"
                v-model="event.doc.event_permalink"
                label="Event Permalink"
                description="Only enter the event endpoint. Events will be rendered at event/<event_permalink>"
            />
            <FormControl
                :type="'select'"
                :options="[
                    {
                        label: 'Being Reviewed',
                        value: 'Being Reviewed'
                    },
                    {
                        label: 'Approved',
                        value: 'Approved'
                    },{
                        label: 'In Progress',
                        value: 'In Progress'
                    },{
                        label: 'Concluded',
                        value: 'Concluded'
                    },{
                        label: 'Cancelled',
                        value: 'Cancelled'
                    },
                ]"
                size="md"
                v-model="event.doc.status"
                label="Event Status"
                description="Current status of the event."
            />
            <FormControl
                :type="'select'"
                :options="eventTypeOptions.data"
                size="md"
                v-model="event.doc.event_type"
                label="Event Type"
            />
            <div class="flex flex-col gap-1">
                <FormControl
                    :type="'checkbox'"
                    size="md"
                    label="Mark as Must Attend"
                    v-model="event.doc.must_attend"
                />
                <span class="text-sm text-gray-600">Mark this event as a must-attend for the audience.</span>
            </div>
            <FormControl
               :type="'text'"
                size="md"
                v-model="event.doc.event_bio"
                label="Short Event Bio"
                description="This bio may be used in OG images and in event cards. Typically it is a one-liner."
            />
            <FormControl
                class="col-span-2"
                :type="'textarea'"
                size="md"
                v-model="event.doc.event_description"
                label="Event Description"
                description="Detailed description of the event. You can use <bold>, <i>, <a> tags for bold, italic, anchor(link) etc respectively."
            />
        </div>
    </div>
    <div class="flex flex-col my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Event Timeline</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
                :type="'datetime-local'"
                v-model="event.doc.event_start_date"
                label="Event Start Date & Time"
                size="md"
            />
            <FormControl
                :type="'datetime-local'"
                v-model="event.doc.event_end_date"
                label="Event End Date & Time"
                size="md"
            />
        </div>
    </div>
    <div class="flex flex-col my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Location Details</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
                :type="'text'"
                label="Location"
                v-model="event.doc.event_location"
                size="md"
            />
            <FormControl
                :type="'url'"
                label="Map Link"
                v-model="event.doc.map_link"
                side="md"
            />
        </div>
    </div>
</div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { createDocumentResource, createListResource, FileUploader, FormControl, Toast } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()
const event = createDocumentResource({
    doctype: 'FOSS Chapter Event',
    name: route.params.id,
    fields: ['*'],
    auto: true,
})

const validateFile = (file) => {
      let extn = file.name.split('.').pop().toLowerCase()
      if (!['png', 'jpg'].includes(extn)) {
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
        banner_image: file.file_url
    })
}

const eventTypeOptions = createListResource({
    doctype: 'FOSS Event Type',
    fields: ['name'],
    auto: true,
    transform(data){
        return data.map(d => {
            return { 'label': d.name, 'value': d.name}
        })
    }
})

let showToast = ref(false)
let toastTitle = ref('')
let toastMessage = ref('')

const updateDetails = () => {
    event.save.submit().then(() => {
        showToastMessage('Success', 'Chapter details updated successfully')
    }).catch((error) => {
        showToastMessage('Error', error.message)
    })
}

const showToastMessage = (title, message) => {
    toastTitle.value = title
    toastMessage.value = message
    showToast.value = true
    setTimeout(() => {
        showToast.value = false
    }, 5000)
}

</script>
