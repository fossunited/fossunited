<template>
  <Button
    @click="toggleSidebar"
    class="block md:hidden absolute bg-white top-14 left-4 z-40 p-4"
    icon="menu"
    theme="subtle"
  />
  <div
    class="hidden w-80 z-10 h-screen absolute md:relative md:flex px-4 py-6 md:h-fill md:w-1/5 bg-white border-r flex-col transition-all duration-300 ease-in-out"
    id="sidebar"
    :class="smallScreen ? 'hidden w-80 z-30 absolute' : ''"
  >
    <div class="font-fff text-sm leading-relaxed mt-5 md:mt-0">
      {{ props.title }}
    </div>
    <div class="my-4">
      <router-link
        to="/"
        class="p-2 flex font-medium gap-2 text-base rounded-sm text-gray-800 hover:underline hover:text-gray-900"
      >
        <FeatherIcon name="arrow-left" class="h-4" />
        <span> Go to Home </span>
      </router-link>
    </div>
    <div class="flex flex-col gap-2">
      <router-link
        v-for="(menuItem, index) in props.menuItems"
        :key="index"
        :to="menuItem.route"
        :class="
          isMenuItemActive(menuItem.route, index)
            ? 'font-semibold text-gray-900 bg-gray-100'
            : ''
        "
        class="block p-2 text-base rounded-sm text-gray-800 hover:bg-gray-200 hover:text-gray-900"
      >
        {{ menuItem.label }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { defineProps, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'

const route = useRoute()
const props = defineProps({
  title: {
    type: String,
    default: 'Organizer Dashboard',
  },
  menuItems: {
    type: Array,
    default: () => [],
  },
})

const isMenuItemActive = (menuRoute, index) => {
  if (index == 0 && menuRoute != route.path) {
    return false
  }
  return menuRoute === route.path || menuRoute === ('/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/'))
}

let smallScreen = ref(false)
onMounted(() => {
  if (window.innerWidth < 768) {
    smallScreen.value = true
  }
})
const toggleSidebar = () => {
  document.getElementById('sidebar').classList.toggle('hidden')
}
</script>
