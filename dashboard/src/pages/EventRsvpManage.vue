<template>
<div v-if="event_rsvp.data">
    <div class="px-4 py-8 md:p-8">
        <div class="text-xl font-medium">Manage RSVP</div>
        <div class="py-4 grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <div>
                <div v-if="rsvp_exists">
                    <Card
                        :class="event_rsvp.data.is_published ? 'text-green-600' : '' "
                        :title="event_rsvp.data.is_published ? 'Form Status: Live!' : 'Form Status: Unpublished'"
                    >
                    <template v-if="event_rsvp.data.is_published" #actions-left>
                        <span class="relative flex h-3 w-3 mr-2">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                        </span>
                    </template>
                    </Card>
                </div>
                <div v-else>
                    <Card
                        title="RSVP form not created."
                        subtitle="No RSVP form has been created for this event."
                    >
                        <Button
                            size="md"
                            icon-left="file-plus"
                            label="Create RSVP Form"
                            @click="() => $router.push(`/event/${event.doc.name}/rsvp/create`)"
                        />
                    </Card>
                </div>
            </div>
            <Switch
                class="mt-3"
                size="md"
                label="Show RSVP Tab"
                v-model="event.doc.show_rsvp"
                description="Show RSVP section on the event page."
                @click="toggleRSVPSection()"
            />
        </div>
    </div>
</div>
</template>
<script setup>
import { createDocumentResource, createResource, FormControl, Switch, Tabs } from 'frappe-ui';
import { reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute()
const event = createDocumentResource({
    doctype: 'FOSS Chapter Event',
    name: route.params.id,
    fields: ['*'],
    auto: true,
})

let rsvp_exists = ref(false)
let event_rsvp = reactive({})

watch(event, (newEvent) => {
    event_rsvp = createResource({
        url: 'frappe.client.get',
        params: {
            doctype: 'FOSS Event RSVP',
            filters: {
                event: newEvent.doc.event
            }
        },
        auto: true,
        onError(error){
            if (error.response.status === 404) {
                rsvp_exists.value = false
            }
        },
        onSuccess(response){
            rsvp_exists.value = true
        }
    })
})

const toggleRSVPSection = () => {
    event.setValue.submit({
        show_rsvp: event.doc.show_rsvp
    })
}
</script>
