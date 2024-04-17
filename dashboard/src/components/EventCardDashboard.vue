<template>
    <Card :title="event.event_name" class="hover:border-2 hover:border-gray-500 transition-all hover:cursor-pointer">
        <div class="flex justify-between">
        <div class="text-sm font-medium">
            {{ event.chapter_name }}
        </div>
        <Badge
            :variant="'subtle'"
            :theme="badgeColors[event.status]"
            :label="event.status"
        ></Badge>
        </div>
        <div class="text-sm font-medium">
        {{ new Date(event.event_start_date).toLocaleDateString('en-IN', { day: 'numeric', month:'long', year: 'numeric'}) }}
        </div>
    </Card>
</template>
<script setup>
import { Card, Badge } from 'frappe-ui'

const badgeColors = {
    'Being Reviewed': 'orange',
    'Approved': 'green',
    'In Progress': 'blue',
    'Concluded': 'gray',
    'Cancelled': 'red',
}
defineProps({
    event: Object
})
</script>
