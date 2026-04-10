<template>
  <div class="relative" @mouseleave="closeExpanded">
    <!-- Compact 60px card: click = ICS download, hover = expand detail -->
    <div
      class="h-[60px] bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-[16px] flex items-center gap-2 px-2 cursor-pointer select-none overflow-hidden"
      :title="`Download .ics for: ${session.title}`"
      @click="handleClick"
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

    <!-- Expanded detail (hover desktop / first-tap mobile) — click downloads ICS -->
    <Transition name="fade-up">
      <div
        v-if="isExpanded"
        class="absolute left-0 top-full mt-1 z-50 w-72 bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-xl shadow-lg p-3 cursor-pointer"
        @click.stop="navigateToCfp"
      >
        <div class="flex gap-3 items-start">
          <div
            v-if="speakers.length"
            class="shrink-0 size-14 overflow-hidden rounded-lg border border-outline-gray-2 grid gap-0.5"
            :class="speakerGridClass"
          >
            <img
              v-for="(speaker, i) in visibleSpeakers"
              :key="i"
              :src="speaker.photo || ''"
              :alt="speaker.full_name || ''"
              class="w-full h-full object-cover object-top"
              loading="lazy"
              @error="(e) => (e.target.style.display = 'none')"
            />
          </div>
          <div class="flex flex-col gap-1.5 min-w-0">
            <h4 class="text-sm font-semibold leading-snug text-ink-gray-9 line-clamp-3">
              {{ session.title }}
            </h4>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="(speaker, i) in speakers"
                :key="i"
                class="text-xs px-2 py-0.5 rounded bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-6 font-medium whitespace-nowrap"
              >
                {{ speaker.full_name }}
              </span>
            </div>
          </div>
        </div>
        <div class="mt-2 flex items-center gap-1.5 flex-wrap">
          <span
            v-if="sessionDuration"
            class="text-xs px-2 py-0.5 rounded bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-5 font-semibold uppercase"
          >
            {{ sessionDuration }}
          </span>
          <span
            v-if="showCategory"
            class="text-xs px-2 py-0.5 rounded font-semibold uppercase"
            :class="categoryStyle"
          >
            {{ sessionCategory }}
          </span>
        </div>
        <p v-if="cfpHref" class="mt-1.5 text-xs text-ink-gray-4 italic">Click to view →</p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import { useSession } from '@/composables/useSession'

const props = defineProps({
  session: { type: Object, required: true },
})

const {
  formatTime,
  speakers,
  visibleSpeakers,
  speakerGridClass,
  sessionDuration,
  sessionCategory,
  showCategory,
  categoryStyle,
  cfpHref,
  downloadIcs,
} = useSession(toRef(props, 'session'))

const isExpanded = ref(false)
const isTouchDevice = typeof window !== 'undefined' && window.matchMedia('(hover: none)').matches

function openExpanded() {
  if (!isTouchDevice) isExpanded.value = true
}
function closeExpanded() {
  if (!isTouchDevice) isExpanded.value = false
}

function handleClick() {
  if (isTouchDevice) {
    // First tap: expand; second tap: navigate to CFP
    if (isExpanded.value) {
      navigateToCfp()
      isExpanded.value = false
    } else isExpanded.value = true
  } else {
    downloadIcs()
  }
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
