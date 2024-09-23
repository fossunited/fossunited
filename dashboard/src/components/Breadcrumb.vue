<template>
  <div class="flex gap-1 items-center">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="text-base flex gap-1 items-center my-2"
      :class="index == items.length - 1 ? 'font-medium text-gray-800' : 'text-gray-600 '"
    >
      <router-link
        v-if="item.route"
        class="hover:text-gray-700 transition-colors"
        :to="item.route"
      >
        {{ item.label }}
      </router-link>
      <a v-else-if="item.link" :href="item.link" class="hover:text-gray-700 transition-colors">
        {{ item.label }}
      </a>
      <span v-else>
        {{ item.label }}
      </span>
      <span v-if="index !== items.length - 1">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler h-4 w-4 icons-tabler-outline icon-tabler-chevron-right"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M9 6l6 6l-6 6" />
        </svg>
      </span>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
})
</script>
