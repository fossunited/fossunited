<template>
    <Header />
    <div class="flex">
        <AppSideBar title="MANAGE CHAPTER" :menuItems="sidebarMenuItems"></AppSideBar>
        <RouterView/>
    </div>
</template>

<script setup>
import AppSideBar from '@/components/AppSidebar.vue'
import Header from '@/components/Header.vue'
import { useRoute, RouterView } from 'vue-router'

const route = useRoute()

const sidebarMenuItems = [
    {
        label: 'Details',
        route: `/chapter/${route.params.id}`
    },
    {
        label: 'Events',
        route: `/chapter/${route.params.id}/events`
    },
    {
        label: 'Members',
        route: `/chapter/${route.params.id}/members`
    },
]
</script>
