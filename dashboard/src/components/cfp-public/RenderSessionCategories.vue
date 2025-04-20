<template>
  <div class="space-y-2">
    <label class="text-base font-medium text-gray-600">Session Categories</label>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(category, index) in categories"
        :key="index"
        class="p-2 flex gap-2 items-center text-sm rounded border border-gray-500 text-ink-gray-6 bg-gray-50"
      >
        {{ category }}
      </div>
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
