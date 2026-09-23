<template>
  <div class="flex flex-col md:flex-row">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:bg-surface-white focus:text-ink-gray-9 focus:px-3 focus:py-2 focus:rounded focus:shadow-lg"
    >
      Skip to main content
    </a>
    <SideNavbar v-if="navItems.data" :menu-items="navItems.data" />
    <main id="main-content" tabindex="-1" class="flex-1 min-w-0 transition-colors duration-300">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { inject, ref } from 'vue'
import { usePageMeta, createResource } from 'frappe-ui'
import SideNavbar from '@/components/NewAppSidebar.vue'

const session = inject('$session')

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
