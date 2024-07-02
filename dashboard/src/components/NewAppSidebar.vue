<template>
  <div
    v-if="nav_items.data"
    class="relative block min-h-0 flex-shrink-0 overflow-hidden hover:overflow-auto"
  >
    <div
      class="fixed flex min-h-screen w-[220px] flex-col border-r bg-gray-50"
    >
      <div class="p-4">
        <!-- <FOSSUnitedLogo class="w-16 h-12" fill="black"></FOSSUnitedLogo> -->
        <div class="font-fff text-gray-900 uppercase">FOSS United</div>
        <div class="text-sm mt-2 tracking-wider text-gray-700 uppercase">
          Dashboard
        </div>
      </div>
      <div class="flex flex-col gap-2 px-4 my-2" v-if="nav_items.data">
        <div v-for="group in nav_items.data" class="my-1">
          <div
            class="text-xs text-gray-600 font-medium uppercase tracking-wide"
          >
            {{ group.parent_label }}
          </div>
          <div class="flex flex-col my-1 text-gray-600">
            <router-link
              v-for="(item, index) in group.items"
              :key="item.label"
              :to="item.route"
              class="w-full text-sm rounded-sm p-2 hover:bg-gray-100 "
              :class="
                isMenuItemActive(item.route, index)
                  ? 'font-medium text-gray-900 bg-gray-100'
                  : ''
              "
            >
              {{ item.label }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import FOSSUnitedLogo from '@/components/FossUnitedLogo.vue'
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()

const nav_items = createResource({
  url: 'fossunited.api.sidebar.get_sidebar_items',
  auto: true,
})

const isMenuItemActive = (menuRoute, index) => {
  if (index == 0 && menuRoute != route.path) {
    return false
  }
  return (
    menuRoute === route.path ||
    menuRoute ===
      '/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/')
  )
}
</script>
