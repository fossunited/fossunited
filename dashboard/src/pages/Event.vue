<template>
  <div class="flex flex-col md:flex-row">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:bg-surface-white focus:text-ink-gray-9 focus:px-3 focus:py-2 focus:rounded focus:shadow-lg"
    >
      Skip to main content
    </a>
    <SideNavbar title="Manage Event" :menu-items="sidebarMenuItems" />
    <main id="main-content" tabindex="-1" class="flex-1 min-w-0 overflow-x-hidden">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, provide, watch } from 'vue'
import { createResource, usePageMeta, createDocumentResource } from 'frappe-ui'
import { RouterView, useRoute } from 'vue-router'
import SideNavbar from '@/components/NewAppSidebar.vue'

const route = useRoute()

const sidebarMenuItems = ref([
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Home',
        route: '/chapter',
      },
    ],
  },
])

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  auto: true,
})

watch(
  () => event.doc,
  (doc) => {
    if (doc) {
      // If sidebar items already set, don't append items again
      if (sidebarMenuItems.value.length > 1) {
        return
      }
      chapter.fetch()
      let sidebar_items = {
        items: [
          {
            icon: 'info',
            label: 'Details',
            route: `/event/${route.params.id}`,
          },
          {
            icon: 'check-circle',
            label: 'RSVP',
            route: `/event/${route.params.id}/rsvp`,
          },
          {
            icon: 'mic',
            label: 'CFP',
            route: `/event/${route.params.id}/cfp`,
          },
          {
            icon: 'clock',
            label: 'Schedule',
            route: `/event/${route.params.id}/schedule`,
          },
          {
            icon: 'briefcase',
            label: 'Partners',
            route: `/event/${route.params.id}/partner`,
          },
          {
            icon: 'monitor',
            label: 'Project Showcases',
            route: `/event/${route.params.id}/showcases`,
          },
          {
            icon: 'heart',
            label: 'Volunteers',
            route: `/event/${route.params.id}/volunteers`,
          },
          {
            icon: 'mail',
            label: 'Mailing',
            route: `/event/${route.params.id}/mailing`,
          },
        ],
      }

      if (doc.is_paid_event) {
        sidebar_items.items.splice(1, 1, {
          icon: 'tag',
          label: 'Tickets',
          route: `/event/${route.params.id}/tickets`,
        })
        sidebar_items.items.push({
          icon: 'user-check',
          label: 'Check-Ins',
          route: `/event/${route.params.id}/checkins`,
        })
        sidebar_items.items.push({
          icon: 'zap',
          label: 'Quick-Checkin',
          route: `/event/${route.params.id}/quick-checkin`,
        })
      }

      sidebarMenuItems.value = [...sidebarMenuItems.value, sidebar_items]
    }
  },
)

provide('event', event)

const chapter = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      fieldname: ['*'],
      filters: { name: event.doc.chapter },
    }
  },
})

provide('chapter', chapter)

usePageMeta(() => {
  return {
    title: 'Manage Event',
  }
})
</script>
