<template>
  <div class="flex">
    <SideNavbar
      title="Manage Event"
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
import { RouterView, useRoute } from 'vue-router'
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
        route: '/chapter'
      }
    ]
  },
  {
    items: [
      {
        label: 'Details',
        route: `/event/${route.params.id}`,
      },
      {
        label: 'RSVP',
        route: `/event/${route.params.id}/rsvp`,
      },
      {
        label: 'CFP',
        route: `/event/${route.params.id}/cfp`,
      },
      {
        label: 'Volunteers',
        route: `/event/${route.params.id}/volunteers`,
      },
    ],
  },
]

usePageMeta(() => {
  return {
    title: 'Manage Event',
  }
})
</script>
