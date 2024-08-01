<template>
  <div class="flex">
    <SideNavbar v-if="nav_items.data" :menuItems="nav_items.data" :class="showNav ? 'z-50 block mt-[55px]' : 'hidden md:block'" />
    <div class="w-full md:ml-[220px]">
      <HeaderWithNav @toggleSidebar="($event) => (showNav = $event)" />
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { inject, watch, ref } from 'vue'
import { usePageMeta, createResource } from 'frappe-ui'
import SideNavbar from '@/components/NewAppSidebar.vue'
import HeaderWithNav from '@/components/HeaderWithNav.vue'

const session = inject('$session')
const showNav = ref(false)

const nav_items = createResource({
  url: 'fossunited.api.sidebar.get_sidebar_items',
  auto: true,
})

usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
