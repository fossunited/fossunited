<template>
  <div class="w-full my-6">
    <!-- Fake scrollbar container at the top -->
    <div
      ref="scrollTop"
      class="overflow-x-scroll scrollbar-thick scrollbar-thumb-black-800 scrollbar-track-gray-300 mb-4"
      @scroll="syncScroll('top')"
    >
      <div :style="{ width: scrollWidth + 'px' }" class="h-4"></div>
    </div>

    <!-- original container, now scroll-disabled -->
    <div
      ref="scrollMain"
      class="flex gap-4 w-full"
      :class="{
        'flex-col': view === 'vertical',
        'flex-row min-h-[800px]': view === 'horizontal',
      }"
      style="overflow-x: scroll"
      @scroll="syncScroll('main')"
    >
      <div
        v-for="(sessions, hall) in schedule"
        :key="hall"
        :class="{
          'flex-shrink-0 basis-1/2': view === 'horizontal',
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
  </div>
</template>

<script setup>
import { defineProps, ref, computed, watch, onMounted, nextTick } from 'vue'
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
const scrollTop = ref(null)
const scrollMain = ref(null)
const scrollWidth = ref(0)

const syncScroll = (source) => {
  if (source === 'top') {
    scrollMain.value.scrollLeft = scrollTop.value.scrollLeft
  } else if (source === 'main') {
    scrollTop.value.scrollLeft = scrollMain.value.scrollLeft
  }
}

onMounted(() => {
  nextTick(() => {
    // Measure actual scrollable width from scrollMain’s content
    scrollWidth.value = scrollMain.value.scrollWidth
  })
})
</script>
