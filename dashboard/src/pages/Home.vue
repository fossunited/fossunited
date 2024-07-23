<template>
  <div class="flex">
    <SideNavbar :class="showNav ? 'z-50 block mt-[55px]' : 'hidden md:block'" />
    <div class="w-full md:ml-[220px]">
      <HeaderWithNav @toggleSidebar="($event) => (showNav = $event)" />
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { inject, watch, ref } from 'vue'
import { usePageMeta } from 'frappe-ui'
import SideNavbar from '@/components/NewAppSidebar.vue'
import HeaderWithNav from '@/components/HeaderWithNav.vue'

const session = inject('$session')
const showNav = ref(false)

usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
