<template>
  <div
    class="flex gap-4 w-full my-6"
    :class="{
      'flex-col': view === 'vertical',
      'overflow-x-scroll flex-row min-h-[800px]': view === 'horizontal',
    }"
  >
    <div
      v-for="(sessions, hall) in schedule"
      :key="hall"
      :class="{
        'min-w-[720px] flex-shrink-0': view === 'horizontal',
      }"
    >
      <SessionListHeader
        :title="hall"
        :collapsible="isCollapsible"
        @collapse-hall="toggleCollapse(hall)"
      />
      <SessionList
        v-if="!isCollapsed(hall)"
        :sessions="sessions"
        :view="view"
      />
    </div>
  </div>
</template>
<script setup>
import { defineProps, ref, computed } from 'vue'
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
  view: {
    type: String,
    required: true,
    default: 'vertical',
  },
})

const isCollapsible = computed(() => props.view === 'vertical')

const collapsedHalls = ref({})

const toggleCollapse = (hall) => {
  collapsedHalls.value[hall] = !collapsedHalls.value[hall]
}

const isCollapsed = (hall) => {
  return collapsedHalls.value[hall] || false
}
</script>
