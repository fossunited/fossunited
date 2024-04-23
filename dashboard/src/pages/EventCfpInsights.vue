<template>
<div v-if="submissions.data && cfp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 my-2">
        <div class="text-xl font-medium">Insights</div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <Card
                :title="`Total Submissions: ${submissions.data.length}`"
            />
        </div>
    </div>
    <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <Button
                class="w-fit"
                size="md"
                label="Download"
                icon-left="download"
                @click="downloadProposalList"
            />
            <span class="text-sm text-gray-500">
                Download the list of proposals for the event.
            </span>
        </div>
        <ListView
            class="w-64"
            :columns="[
                { label: 'Talk Title', key: 'talk_title', width: 2 },
                { label: 'Submitter', key: 'full_name' },
                { label: 'Status', key: 'status'},
                { label: 'Session Type', key: 'session_type'}
            ]"
            :rows="submissions.data"
            row-key="name"
            :options="{
                selectable: false,
                emptyState: {
                    title: 'No Submissions Yet',
                    description: 'There are no CFP submissions for this event yet.'
                },
                resizeColumn: true,
                onRowClick: (row) => {
                    handleProposalClick(row)
                }
            }"
        />
    </div>
    <Dialog
        v-model="showProposalDialog"
        :options="{
            title: 'Proposal Details',
            size: 'xl',
        }"
    >
        <template #body-content>
            <div v-if="selected_row_data.get.loading">
                <data class="text-sm text-gray-600">Loading...</data>
            </div>
            <div v-else class="flex flex-col gap-6">
                <div class="flex flex-col gap-4">
                    <div class="flex flex-col md:flex-row justify-between items-baseline mb-1 pb-2 border-b">
                        <div class="text-lg font-semibold">
                            Status: <span :class=" selected_row_data.doc.status == 'Approved' ? 'text-green-600' : (selected_row_data.doc.status == 'Rejected' ? 'text-red-600' : 'text-orange-500')">{{ selected_row_data.doc.status }}</span>
                        </div>
                        <Button
                            theme="red"
                            icon-left="trash"
                            label="Delete"
                            @click="deleteSubmission"
                        />
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                        <div>
                            <div class="font-semibold text-gray-800">Positive Reviews</div>
                            <div>{{ selected_row_data.doc.positive_reviews }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Negative Reviews</div>
                            <div>{{ selected_row_data.doc.negative_reviews }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Unsure Reviews</div>
                            <div>{{ selected_row_data.doc.unsure_reviews }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Approvability</div>
                            <div>{{ selected_row_data.doc.approvability }}%</div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 items-end">
                        <FormControl
                            label="Change Status"
                            type="select"
                            size="md"
                            v-model="selected_row_data.doc.status"
                            :options="[
                                {
                                    label: 'Approved',
                                    value: 'Approved'
                                },
                                {
                                    label: 'Rejected',
                                    value: 'Rejected'
                                },
                                {
                                    label: 'Review Pending',
                                    value: 'Review Pending'
                                }
                            ]"
                        />
                        <Button
                            :variant="'solid'"
                            size="md"
                            label="Update Status"
                            @click="setCfpStatus"
                        />

                    </div>
                </div>
                <div class="flex flex-col gap-4">
                    <div class="flex flex-col mb-4 gap-2">
                        <div class="text-lg font-semibold mb-1 pb-2 border-b">Session Details</div>
                        <div>
                            <div class="font-semibold text-gray-800">Session Title</div>
                            <div>{{ selected_row_data.doc.talk_title }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Session Type</div>
                            <div>{{ selected_row_data.doc.session_type }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Session Description</div>
                            <div>{{ selected_row_data.doc.talk_description }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Is a first talk?</div>
                            <div>{{ selected_row_data.doc.is_first_talk }}</div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Session Reference</div>
                            <a :href="selected_row_data.doc.talk_reference" target="_blank">{{ selected_row_data.doc.talk_reference }}</a>
                        </div>
                    </div>
                    <div v-if="selected_row_data.doc.custom_answers.length > 0" class="flex flex-col mb-4 gap-2">
                        <div class="text-lg font-semibold mb-1 pb-2 border-b">Custom Question</div>
                        <div v-for="response in selected_row_data.doc.custom_answers">
                            <div class="font-semibold text-gray-800">{{ response.question }}</div>
                            <div>{{ response.response }}</div>
                        </div>
                    </div>
                    <div class="flex flex-col mb-4 gap-2">
                        <div class="text-lg font-semibold mb-1 pb-2 border-b">Submitter Details</div>
                        <div v-if="selected_row_data.doc.picture_url">
                            <div class="font-semibold text-gray-800 mb-1">Photo</div>
                            <div class="flex flex-col gap-2">
                                <img :src="selected_row_data.doc.picture_url" alt="Submitted Image" class="w-32 object-cover aspect-square rounded-sm">
                                <Button
                                    class="w-fit"
                                    size="md"
                                    label="Open Image Link"
                                    icon-left="external-link"
                                    @click="openImageLink(selected_row_data.doc.picture_url)"
                                />
                            </div>
                        </div>
                        <div class="grid gap-2 grid-cols-1 md:grid-cols-2">
                            <div>
                                <div class="font-semibold text-gray-800">Submitter</div>
                                <div>{{ selected_row_data.doc.full_name }}</div>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-800">Email</div>
                                <div>{{ selected_row_data.doc.email }}</div>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-800">Designation</div>
                                <div>{{ selected_row_data.doc.designation }}</div>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-800">Organization</div>
                                <div>{{ selected_row_data.doc.organization }}</div>
                            </div>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-800">Bio</div>
                            <div>{{ selected_row_data.doc.bio }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Dialog>
</div>
</template>
<script setup>
import { createListResource, createResource, ListView, Dialog, createDocumentResource, Button, FormControl } from 'frappe-ui';
import { ref, reactive } from 'vue';
import { toast } from 'vue-sonner';
import { useRoute } from 'vue-router';

const route = useRoute()

const cfp_form = createResource({
    url: 'frappe.client.get',
    params: {
        doctype: 'FOSS Event CFP',
        fields: ["*"],
        filters: {
            event: route.params.id,
        }
    },
    auto:true
})

const submissions = createListResource({
    doctype: 'FOSS Event CFP Submission',
    fields: ['*'],
    filters: {
        event: route.params.id
    },
    pageLength: 99999,
    auto: true,
})

let selectedProposal = ref(null)
let showProposalDialog = ref(false)
let selected_row_data = reactive({})

const handleProposalClick = (row) => {
    selected_row_data = createDocumentResource({
        doctype: 'FOSS Event CFP Submission',
        name: row.name,
        fields: ['*'],
        auto: true,
    })
    selectedProposal.value = row
    showProposalDialog.value = true
}

const openImageLink = (url) => {
    window.open(url, '_blank')
}

const setCfpStatus = () => {
    selected_row_data.setValue.submit({
        status: selected_row_data.doc.status
    }).then(() => {
        toast.success('Status updated successfully')
    }).catch((err) => {
        toast.error('Failed to update status', {
            description: err.message
        })
    })
}

const deleteSubmission = () => {
    showProposalDialog.value = false
    selected_row_data.delete.submit().then(() => {
        toast.success('Submission deleted successfully')
    }).catch((err) => {
        toast.error('Failed to delete submission', {
            description: err.message
        })
    })
    selected_row_data = {}
}

const downloadProposalList = () => {
    // ToDo: Implement Frappe exporter for this

    const csv = submissions.data.map(submission => {
        let customResponses = [];
        if (submission.custom_answers) {
            customResponses = submission.custom_answers.map(response => [
                response.question,
                response.response
            ]);
        }

        return [
            submission.talk_title,
            submission.session_type,
            submission.is_first_talk,
            submission.talk_reference,
            submission.talk_description,
            submission.full_name,
            submission.first_name,
            submission.last_name,
            submission.email,
            submission.picture_url,
            submission.designation,
            submission.organization,
            submission.bio,
        ]
    })
    csv.unshift([
        'Talk Title',
        'Session Type',
        'Is First Talk',
        'Talk Reference',
        'Talk Description',
        'Full Name',
        'First Name',
        'Last Name',
        'Email',
        'Picture URL',
        'Designation',
        'Organization',
        'Bio',
    ])
    const csvContent = "data:text/csv;charset=utf-8," + csv.map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "proposal_list.csv");
    document.body.appendChild(link);
    link.click();
}

</script>
