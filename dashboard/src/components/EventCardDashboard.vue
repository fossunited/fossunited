<template>
    <Card :title="event.event_name" class="hover:border-2 hover:border-gray-500 transition-all hover:cursor-pointer">
        <div class="flex justify-between">
        <div class="text-sm font-medium">
            {{ event.chapter_name }}
        </div>
        <Badge
            :variant="'subtle'"
            :theme="event.status == 'Being Reviewed' ? 'orange' : 'green'"
            :label="event.status"
        ></Badge>
        </div>
        <div class="text-sm font-medium">
        {{ event.event_start_date }}
        </div>
    </Card>
</template>
<script setup>
import { Card, Badge } from 'frappe-ui'
defineProps({
    event: Object
})
</script>
