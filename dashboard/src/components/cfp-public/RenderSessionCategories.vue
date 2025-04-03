<template>
  <div class="flex flex-wrap gap-2">
    <div
      v-for="(category, index) in categories"
      :key="index"
      class="p-2 flex gap-2 items-center text-sm rounded border border-gray-500 text-ink-gray-6 bg-gray-50"
    >
      {{ category }}
    </div>
  </div>
</template>
<script setup>
defineProps({
  categories: {
    type: Array,
    required: true,
  },
})
</script>
