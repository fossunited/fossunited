<template>
  <div class="flex">
    <SideNavbar
      v-if="navItems.data"
      :menu-items="navItems.data"
      :class="showNav ? 'z-50 block mt-[55px]' : 'hidden md:block'"
    />
    <div class="w-full md:ml-[220px]">
      <HeaderWithNav @toggle-sidebar="($event) => (showNav = $event)" />
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

const navItems = createResource({
  url: 'fossunited.api.sidebar.get_sidebar_items',
  makeParams() {
    return {
      user: session.user,
    }
  },
  auto: true,
})

usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
