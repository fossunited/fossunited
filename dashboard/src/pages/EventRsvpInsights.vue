<template>
<div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 my-2">
        <div class="text-xl font-medium">RSVP Insights</div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <Card
                :title="`Total Submissions: ${submissions.data.length}`"
                :subtitle="`out of ${rsvp_form.data.max_rsvp_count}`"
            />
        </div>
    </div>
    <div class="flex flex-col gap-4">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Attendee List</div>
        <div class="flex flex-col gap-2">
            <Button
                class="w-fit"
                size="md"
                label="Download List"
                icon-left="download"
                @click="downloadAttendeeList"
            />
            <span class="text-sm text-gray-500">
                Download the list of attendees who have RSVPed for the event.
            </span>
        </div>
        <ListView
            :columns="[
                { label: 'Name', key: 'name1' },
                { label: 'Email', key: 'submitted_by' },
                { label: 'I am a', key: 'im_a' },
            ]"
            :rows="submissions.data"
            row-key="name"
            :options="{
                selectable: false,
                emptyState: {
                    title: 'No Submissions Yet',
                    description: 'No one has RSVPed for the event yet.'
                }
            }"
        />
    </div>
</div>
</template>
<script setup>
import { createListResource, createResource, ListView } from 'frappe-ui';
import { useRoute } from 'vue-router';

const route = useRoute()

const rsvp_form = createResource({
    url: 'frappe.client.get',
    params: {
        doctype: 'FOSS Event RSVP',
        fields: ["*"],
        filters: {
            event: route.params.id,
        }
    },
    auto:true
})

const submissions = createListResource({
    doctype: 'FOSS Event RSVP Submission',
    fields: ['*'],
    filters: {
        event: route.params.id
    },
    page_length: 99999,
    auto: true,
    transform(data){
        data.forEach(submission => {
            submission.submitted_by = submission.submitted_by.replace(/(?<=.{3}).(?=[^@]*?@)/g, '*')
        })
    }
})

const downloadAttendeeList = () => {
    const csv = submissions.data.map(submission => {
        return [
            submission.name1,
            submission.submitted_by,
            submission.im_a
        ].join(',')
    }).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Attendee List-${rsvp_form.data.event_name}-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
}
</script>
