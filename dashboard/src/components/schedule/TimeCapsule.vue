<template>
  <div
    class="relative outline-none"
    tabindex="0"
    @mouseleave="closeExpanded"
    @blur="isExpanded = false"
  >
    <!-- Compact 60px card: hover expands, click navigates to CFP -->
    <div
      class="h-[60px] bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-[16px] flex items-center gap-2 px-2 cursor-pointer select-none overflow-hidden"
      :title="session.title"
      @click="handleClick($event)"
      @mouseenter="openExpanded"
    >
      <div
        class="shrink-0 h-11 px-2.5 rounded-lg bg-surface-gray-7 text-ink-white text-xs font-semibold uppercase flex items-center whitespace-nowrap"
      >
        {{ formatTime(session.start_time) }}
      </div>
      <p class="text-xs text-ink-gray-9 font-normal leading-snug line-clamp-2 flex-1 min-w-0">
        {{ session.title }}
      </p>
    </div>

    <!-- Expanded detail: full SessionCard preview -->
    <Transition name="fade-up">
      <div
        v-if="isExpanded"
        class="absolute left-0 top-full z-50 w-auto shadow-xl bg-surface-white dark:bg-surface-gray-2 rounded-[16px] px-2 md:px-4"
        @click.stop
      >
        <SessionCard :session="session" preview />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import { useSession } from '@/composables/useSession'
import SessionCard from '@/components/schedule/SessionCard.vue'

const props = defineProps({
  session: { type: Object, required: true },
})

const { formatTime, cfpHref } = useSession(toRef(props, 'session'))

const isExpanded = ref(false)
const isTouchDevice = typeof window !== 'undefined' && window.matchMedia('(hover: none)').matches

function openExpanded() {
  if (!isTouchDevice) isExpanded.value = true
}
function closeExpanded() {
  if (!isTouchDevice) isExpanded.value = false
}

function handleClick(e) {
  if (isTouchDevice && !isExpanded.value) {
    isExpanded.value = true
    e.currentTarget.focus()
    return
  }
  navigateToCfp()
  isExpanded.value = false
}

function navigateToCfp() {
  if (cfpHref.value) window.open(cfpHref.value, '_blank')
}
</script>

<style scoped>
.fade-up-enter-active,
.fade-up-leave-active {
  transition:
    opacity 0.12s ease,
    transform 0.12s ease;
}
.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
