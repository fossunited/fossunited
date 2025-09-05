<template>
  <div class="w-full my-6 relative">
    <!-- Fake scrollbar container at the top -->
    <div
      v-if="view === 'horizontal'"
      ref="scrollTop"
      aria-hidden="true"
      role="presentation"
      class="overflow-x-scroll scrollbar-thick scrollbar-thumb-gray-800 scrollbar-track-gray-300 mb-4"
      @scroll="syncScroll('top')"
    >
      <div :style="{ width: scrollWidth + 'px' }" class="h-4"></div>
    </div>

    <div
      ref="scrollMain"
      class="flex gap-4 w-full relative"
      :class="{
        'flex-col': view === 'vertical',
        'flex-row overflow-x-scroll min-h-[800px]': view === 'horizontal',
      }"
      @scroll="syncScroll('main')"
    >
      <!-- Your sessions -->
      <div
        v-for="hall in orderedHalls"
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
        <SessionList v-if="!isCollapsed(hall)" :sessions="schedule[hall]" :view="view" />
      </div>

      <!-- Shadow indicator -->
    </div>
    <div
      v-if="view === 'horizontal' && showRightShadow"
      class="absolute mt-10 top-0 right-0 h-full pointer-events-none w-16 transition-opacity duration-300"
      style="background: linear-gradient(to left, #a4a4a4, transparent)"
    ></div>
  </div>
</template>

<script setup>
import { defineProps, ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import SessionList from '@/components/schedule/SessionList.vue'
import SessionListHeader from '@/components/schedule/SessionListHeader.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true,
  },
  view: {
    type: String,
    required: true,
    default: 'vertical',
  },
})

const isCollapsible = computed(() => props.view === 'vertical')

const orderedHalls = computed(() => Object.keys(props.schedule || {}).sort())

const collapsedHalls = ref({})

const toggleCollapse = (hall) => {
  if (props.view === 'vertical') {
    collapsedHalls.value[hall] = !collapsedHalls.value[hall]
  }
}

const isCollapsed = (hall) => {
  return props.view === 'vertical' && collapsedHalls.value[hall]
}

watch(
  () => [props.schedule, props.view],
  ([schedule, view]) => {
    if (view === 'vertical' && schedule) {
      collapsedHalls.value = Object.fromEntries(Object.keys(schedule).map((hall) => [hall, true]))
    }
    // Recompute metrics after DOM updates caused by schedule/view changes
    nextTick(() => updateScrollMetrics())
  },
  { immediate: true },
)

const scrollTop = ref(null)
const scrollMain = ref(null)
const scrollWidth = ref(0)

// New reactive state for shadow visibility
const showRightShadow = ref(false)

const updateRightShadow = () => {
  const container = scrollMain.value
  if (!container) return

  const scrollPosition = container.scrollLeft + container.clientWidth
  const scrollThreshold = container.scrollWidth * 0.9

  showRightShadow.value = scrollPosition < scrollThreshold
}

// Prevent re-entrant scroll syncing
const isSyncing = ref(false)

// Keep scrollWidth and shadow in sync with the actual content
const updateScrollMetrics = () => {
  const container = scrollMain.value
  if (!container) return
  scrollWidth.value = container.scrollWidth
  updateRightShadow()
}

const syncScroll = (source) => {
  // Only sync in horizontal view
  if (props.view !== 'horizontal') return
  const topEl = scrollTop.value
  const mainEl = scrollMain.value
  if (!topEl || !mainEl) return
  if (isSyncing.value) return
  isSyncing.value = true

  if (source === 'top') {
    mainEl.scrollLeft = topEl.scrollLeft
  } else if (source === 'main') {
    topEl.scrollLeft = mainEl.scrollLeft
  }
  updateRightShadow()
  requestAnimationFrame(() => {
    isSyncing.value = false
  })
}

onMounted(() => {
  nextTick(() => {
    updateScrollMetrics()
  })

  // Keep metrics in sync on window resize
  window.addEventListener('resize', updateScrollMetrics)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateScrollMetrics)
})
</script>
