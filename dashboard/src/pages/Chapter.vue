<template>
  <div class="flex">
    <SideNavbar
      title="Manage Chapter"
      :menuItems="sidebarMenuItems"
      :class="showNav ? 'z-50 block mt-[55px]' : 'hidden md:block'"
    />
    <div class="w-full md:ml-[220px]">
      <HeaderWithNav @toggleSidebar="($event) => (showNav = $event)" />
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { usePageMeta } from 'frappe-ui'
import { useRoute, RouterView } from 'vue-router'
import SideNavbar from '@/components/NewAppSidebar.vue'
import HeaderWithNav from '@/components/HeaderWithNav.vue'

const route = useRoute()
const showNav = ref(false)

const sidebarMenuItems = [
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Home',
        route: '/chapter',
      },
    ],
  },
  {
    items: [
      {
        label: 'Details',
        route: `/chapter/${route.params.id}`,
      },
      {
        label: 'Events',
        route: `/chapter/${route.params.id}/events`,
      },
      {
        label: 'Members',
        route: `/chapter/${route.params.id}/members`,
      },
    ],
  },
]

usePageMeta(() => {
  return {
    title: 'Manage Chapter',
  }
})
</script>
