<template>
    <Header/>
    <div class="flex">
        <AppSidebar
            title="MANAGE EVENT"
            :menuItems="sidebarMenuItems"
        />
        <RouterView/>
    </div>
</template>

<script setup>
import { RouterView, useRoute } from 'vue-router'
import Header from '@/components/Header.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { usePageMeta } from 'frappe-ui';

const route = useRoute()

const sidebarMenuItems = [
    {
        label: 'Details',
        route: `/event/${route.params.id}`
    },
    {
        label: 'Manage RSVP',
        route: `/event/${route.params.id}/rsvp`
    },
    {
        label: 'Manage CFP',
        route: `/event/${route.params.id}/cfp`
    },
]

usePageMeta(() => {
  return {
    title: 'Manage Event',
  }
})
</script>
