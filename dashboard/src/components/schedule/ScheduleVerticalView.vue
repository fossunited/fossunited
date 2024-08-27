<template>
  <div class="flex flex-col gap-4 w-full my-6">
    <div v-for="(sessions, hall) in schedule" :key="hall">
      <SessionListHeader
        :title="hall"
        :collapsible="true"
        @collapse-hall="toggleCollapse(hall)"
      />
      <SessionList v-if="!isCollapsed(hall)" :sessions="sessions" />
    </div>
  </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import SessionList from '@/components/schedule/SessionList.vue'
import SessionListHeader from '@/components/schedule/SessionListHeader.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true,
  },
  day: {
    type: String,
    required: true,
  },
})

const collapsedHalls = ref({})

const toggleCollapse = (hall) => {
  collapsedHalls.value[hall] = !collapsedHalls.value[hall]
}

const isCollapsed = (hall) => {
  return collapsedHalls.value[hall] || false
}
</script>
