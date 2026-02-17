<template>
  <div class="flex gap-3 border-b px-8 text-ink-gray-5">
    <router-link
      v-for="(tab, index) in tabs"
      :key="index"
      :to="tab.route"
      class="px-4 py-2 text-base transition-[border] hover:border-outline-gray-3 hover:text-ink-gray-9"
      :class="{
        'font-medium border-b-2 border-black text-ink-gray-9 hover:border-outline-gray-5 hover:text-ink-gray-8':
          tab.route === route.path,
      }"
    >
      {{ tab.label }}
    </router-link>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
defineProps({
  tabs: {
    type: Object,
    required: true,
  },
})
</script>
