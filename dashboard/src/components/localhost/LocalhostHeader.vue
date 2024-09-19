<template>
  <div class="prose mt-4">
    <h2>{{ localhost.localhost_name }}</h2>
  </div>
  <div class="flex gap-2 my-2 text-base font-medium items-center">
    <div class="flex gap-1 items-center">
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
        class="icon w-5 h-5 icon-tabler icons-tabler-outline icon-tabler-map-pin"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
        <path
          d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0z"
        />
      </svg>
      {{ localhost.location }}
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})
</script>
