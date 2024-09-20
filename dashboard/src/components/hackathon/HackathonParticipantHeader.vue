<template>
  <img
    v-if="hackathon.data.hackathon_banner && showBanner"
    :src="hackathon.data.hackathon_banner"
    alt=""
    class="w-full h-32 md:h-full md:max-h-72 object-cover rounded-sm"
  />
  <img :src="hackathon.data.hackathon_logo" alt="Logo" class="h-10 md:h-14 mt-6 mb-4" />
  <div
    class="flex gap-4 items-center rounded-sm w-fit py-2 mt-4 font-medium text-base text-gray-900 stroke-gray-900"
  >
    <div class="flex gap-1 justify-center items-center">
      <svg
        v-if="hackathon.data.hackathon_type == 'In-Person'"
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon icon-tabler icons-tabler-outline icon-tabler-map-pin-code"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
        <path
          d="M11.85 21.48a1.992 1.992 0 0 1 -1.263 -.58l-4.244 -4.243a8 8 0 1 1 13.385 -3.585"
        />
        <path d="M20 21l2 -2l-2 -2" />
        <path d="M17 17l-2 2l2 2" />
      </svg>
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon icon-tabler icons-tabler-outline icon-tabler-world"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
        <path d="M3.6 9h16.8" />
        <path d="M3.6 15h16.8" />
        <path d="M11.5 3a17 17 0 0 0 0 18" />
        <path d="M12.5 3a17 17 0 0 1 0 18" />
      </svg>
      <span>{{ hackathon.data.hackathon_type }}</span>
    </div>
    <div>|</div>
    <div class="flex gap-1 justify-center items-center">
      <div>
        {{ formatDate(hackathon.data.start_date) }}
      </div>
      <div v-if="hackathon.data.start_date != hackathon.data.end_date" class="flex gap-1">
        <span>-</span>
        <span>
          {{ formatDate(hackathon.data.end_date) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  hackathon: {
    type: Object,
    default: () => ({}),
  },
  showBanner: {
    type: Boolean,
    default: true,
  },
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>
