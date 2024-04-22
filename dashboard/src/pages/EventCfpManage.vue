<template>
<div v-if="!cfp_exists">
    <div class="px-4 py-8 md:p-8">
    <Card
        title="CFP form not created."
        subtitle="No CFP form has been created for this event."
    >
    <template #actions>
        <Button
            size="md"
            icon-left="file-plus"
            label="Create Form"
            @click="() => $router.push(`/event/${event.doc.name}/cfp/create`)"
        />
    </template>
    </Card>
    </div>
</div>
<div v-if="cfp_exists && event_cfp.data">
    <div class="px-4 py-8 md:p-8">
        <div class="text-xl font-medium">Manage</div>
        <div class="py-4 grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <div>
                <Card
                    :class="event_cfp.data.is_published ? 'text-green-600' : '' "
                    :title="event_cfp.data.is_published ? 'Form Status: Live!' : 'Form Status: Unpublished'"
                >
                <template v-if="event_cfp.data.is_published" #actions-left>
                    <span class="relative flex h-3 w-3 mr-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                </template>
                </Card>
            </div>
            <Switch
                class="mt-3"
                size="md"
                label="Show CFP Tab"
                v-model="event.doc.show_cfp"
                description="Show CFP section on the event page."
                @click="toggleCFPSection()"
            />
        </div>
    </div>
</div>

</template>
<script setup>
import { createDocumentResource, createResource, FormControl, Switch, Tabs } from 'frappe-ui';
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

let cfp_exists = ref(false)
let event_cfp = reactive({})

watch(event, (newEvent) => {
    event_cfp = createResource({
        url: 'frappe.client.get',
        params: {
            doctype: 'FOSS Event CFP',
            filters: {
                event: newEvent.doc.name
            }
        },
        auto: true,
        onError(error){
            if (error.response.status === 404) {
                cfp_exists.value = false
            }
        },
        onSuccess(response){
            cfp_exists.value = true
        }
    })
})

const toggleCFPSection = () => {
    event.setValue.submit({
        show_cfp: event.doc.show_cfp
    })
    if (event.doc.show_cfp) {
        toast.success('CFP section visible on event page.')
    } else {
        toast.info('CFP section hidden on the event page.')
    }
}
</script>
