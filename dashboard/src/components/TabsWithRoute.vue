<template>
  <div class="flex gap-3 border-b px-8 text-gray-600">
    <router-link
      v-for="(tab, index) in tabs"
      :key="index"
      :to="tab.route"
      class="px-4 py-2 text-base transition-[border] hover:border-gray-400 hover:text-gray-900"
      :class="{
        'font-medium border-b-2 border-black text-gray-900 hover:border-gray-900 hover:text-gray-800':
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
