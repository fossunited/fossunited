<script setup>
import { Popover } from 'frappe-ui'
import { computed, onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  submission: {
    type: Object,
    required: true,
  },
})

const scoreTableItems = computed(() => {
  return [
    {
      label: 'Approved',
      value: props.submission.approved_percent,
      color: 'bg-green-400',
    },
    {
      label: 'Rejected',
      value: props.submission.rejected_percent,
      color: 'bg-red-400',
    },
    {
      label: 'Unsure',
      value: props.submission.unsure_percent,
      color: 'bg-orange-400',
    },
  ]
})

const hasScores = computed(() => {
  return (
    props.submission.approved_percent > 0 ||
    props.submission.rejected_percent > 0 ||
    props.submission.unsure_percent > 0
  )
})

// frappe-ui v1's Popover only supports trigger="click" | "manual" — "hover" is
// no longer a recognised value and silently falls through to click behavior.
// Drive it manually to preserve the original hover-to-reveal UX. The #default
// panel is teleported to <body> by PopoverPortal, so it is NOT a descendant of
// the trigger wrapper below in the live DOM — mouseenter/mouseleave must be
// wired on both the trigger wrapper and the panel itself, sharing this same
// ref, so moving the pointer from the trigger into the panel keeps it open
// (mirrors the old 0.1.x Popover's shared pointerOverTargetOrPopup flag).
//
// There's a real ~4px gap between the trigger and the panel (Popover's
// default offset), and the panel unmounts instantly on close (no exit
// animation to buy time). A pointer-movement sample that lands in that gap
// fires mouseleave on the trigger with no panel to re-enter yet, so a plain
// isOpen=false/true pair on each element's own enter/leave is not enough —
// it can still close the panel out from under a normal mouse movement.
// Debounce the close instead (hover-intent pattern): closing schedules
// isOpen=false after a short delay, and either element's mouseenter cancels
// that pending close before it fires.
const isOpen = ref(false)
let closeTimer = null

function openNow() {
  if (closeTimer !== null) {
    clearTimeout(closeTimer)
    closeTimer = null
  }
  isOpen.value = true
}

function closeSoon() {
  if (closeTimer !== null) clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    isOpen.value = false
    closeTimer = null
  }, 150)
}

onBeforeUnmount(() => {
  if (closeTimer !== null) clearTimeout(closeTimer)
})
</script>
<template>
  <div class="inline-block" @mouseenter="openNow" @mouseleave="closeSoon">
    <Popover trigger="manual" v-model:open="isOpen">
      <template #trigger>
        <div v-if="hasScores" class="flex flex-col items-start gap-1 w-32 text-xs p-2">
          <div class="w-full h-1 flex *:rounded-4">
            <div :style="{ width: `${submission.approved_percent}%` }" class="bg-green-400"></div>
            <div :style="{ width: `${submission.rejected_percent}%` }" class="bg-red-400"></div>
            <div :style="{ width: `${submission.unsure_percent}%` }" class="bg-orange-400"></div>
          </div>
        </div>
        <span v-else class="text-ink-gray-5 ml-2">Not yet reviewed</span>
      </template>
      <template #default>
        <div
          class="p-4 bg-surface-base rounded-4 flex flex-col gap-2"
          @mouseenter="openNow"
          @mouseleave="closeSoon"
        >
          <div
            v-for="scoreItem in scoreTableItems"
            :key="scoreItem.label"
            class="flex gap-2 last:border-t last:pt-2"
          >
            <div class="h-4 w-4" :class="scoreItem.color"></div>
            <span class="text-sm-medium">{{ scoreItem.label }}</span>
            <span class="text-sm-medium">{{ scoreItem.value }}%</span>
          </div>
        </div>
      </template>
    </Popover>
  </div>
</template>
