<template>
<div>

</div>
</template>

<script setup>

import { useRoute } from 'vue-router'

import {
    createResource,
    usePageMeta
} from 'frappe-ui'

const route = useRoute()
const eventPermalink = route.params.permalink
usePageMeta(() => {
    return {
        title: 'All proposals' // to be customised
    }
})

const event = createResource({
    url: 'frappe.client.get_value',
    makeParams() {
        return {
            doctype: 'FOSS Chapter Event',
            filters: {'event_permalink': eventPermalink},
            fieldname: [
                'chapter_name',
                'event_name',
                'event_start_date',
                'event_end_date',
                'event_bio',
            ]

        }
    }
})

</script>
