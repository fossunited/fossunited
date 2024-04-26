<template>
<div v-if="!rsvp_exists">
    <div class="px-4 py-8 md:p-8">
    <Card
        title="RSVP form not created."
        subtitle="No RSVP form has been created for this event."
    >
    <template #actions>
        <Button
            size="md"
            icon-left="file-plus"
            label="Create RSVP Form"
            @click="() => $router.push(`/event/${event.doc.name}/rsvp/create`)"
        />
    </template>
    </Card>
    </div>
</div>
<div v-if="rsvp_exists && event_rsvp.data">
    <div class="p-4 md:p-8">
        <div class="py-4 grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
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
import { createDocumentResource, createResource, Switch } from 'frappe-ui';
import { reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { toast } from 'vue-sonner';

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
                event: newEvent.doc.name
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
    if (event.doc.show_rsvp) {
        toast.success('RSVP section visible on event page.')
    } else {
        toast.info('RSVP section hidden on the event page.')
    }
}
</script>
