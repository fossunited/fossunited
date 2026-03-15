<script setup>
import { useTheme } from 'frappe-ui'
import { IconSunHighFilled, IconMoonStars } from '@tabler/icons-vue'

defineProps({
  size: {
    type: Number,
    default: 18,
  },
})

const { currentTheme, toggleTheme } = useTheme()
</script>

<template>
  <button
    class="p-1.5 rounded-md hover:bg-surface-gray-2 transition-colors"
    :title="currentTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
    @click="toggleTheme"
  >
    <IconSunHighFilled v-if="currentTheme === 'dark'" :size="size" :stroke="1.5" />
    <IconMoonStars v-else :size="size" :stroke="1.5" />
  </button>
</template>
