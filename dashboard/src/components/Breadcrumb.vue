<template>
  <div class="flex gap-1 flex-wrap items-center my-2">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="text-base flex gap-1 items-center"
      :class="index == items.length - 1 ? 'font-medium text-ink-gray-8' : 'text-ink-gray-5 '"
    >
      <router-link
        v-if="item.route"
        class="hover:text-ink-gray-6 transition-colors"
        :to="item.route"
      >
        {{ item.label }}
      </router-link>
      <a v-else-if="item.link" :href="item.link" class="hover:text-ink-gray-6 transition-colors">
        {{ item.label }}
      </a>
      <span v-else>
        {{ item.label }}
      </span>
      <span v-if="index !== items.length - 1">
        <IconChevronRight class="w-5" />
      </span>
    </div>
  </div>
</template>
<script setup>
import { IconChevronRight } from '@tabler/icons-vue'
import { defineProps } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
})
</script>
