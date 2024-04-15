<template>
<div class="relative flex px-4 py-6 h-fill w-1/5 border-r flex-col transition-all duration-300 ease-in-out" id="sidebar">
    <div class="font-fff text-sm leading-relaxed">
        {{ props.title }}
    </div>
    <div class="my-4">
        <router-link to="/" class=" p-2 flex font-medium gap-2 text-base rounded-sm text-gray-800 hover:underline hover:text-gray-900">
            <FeatherIcon name="arrow-left" class="h-4" />
            <span>
                Go to Home
            </span>
        </router-link>
    </div>
    <div class=" flex flex-col gap-2">
        <router-link v-for="(menuItem, index) in props.menuItems" :key="index" :to="menuItem.route" :class=" isMenuItemActive(menuItem.route) ? 'font-semibold text-gray-900 bg-gray-100' : ''" class="block p-2 text-base rounded-sm text-gray-800 hover:bg-gray-200 hover:text-gray-900">
        {{ menuItem.label }}
      </router-link>
    </div>
</div>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon } from 'frappe-ui';

const route = useRoute()
const props = defineProps({
    title: {
        type: String,
        default: "Organizer Dashboard",
    },
    menuItems: {
        type: Array,
        default: () => [],
    }
})

const isMenuItemActive = (menuRoute) => {
    return menuRoute === route.path
}
</script>
