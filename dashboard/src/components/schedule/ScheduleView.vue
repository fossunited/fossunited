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
        :view="view"
        @collapse-hall="toggleCollapse(hall)"
      />
      <SessionList v-if="!isCollapsed(hall)" :sessions="sessions" :view="view" />
    </div>
  </div>
</template>
<script setup>
import { defineProps, ref, computed, watch } from 'vue'
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
  if (props.view === 'vertical') {
    collapsedHalls.value[hall] = !collapsedHalls.value[hall]
  }
}

const isCollapsed = (hall) => {
  // Collapse only matters in vertical view
  return props.view === 'vertical' && collapsedHalls.value[hall]
}

watch(
  () => [props.schedule, props.view],
  ([schedule, view]) => {
    if (view === 'vertical' && schedule) {
      collapsedHalls.value = Object.fromEntries(Object.keys(schedule).map((hall) => [hall, true]))
    }
  },
  { immediate: true },
)
</script>
