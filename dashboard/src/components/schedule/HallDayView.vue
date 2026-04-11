<template>
  <div
    class="w-full mt-3 bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-xl overflow-hidden"
  >
    <div
      v-if="halls.length > 0"
      class="sticky top-0 z-30 bg-surface-white dark:bg-surface-gray-2 border-b border-outline-gray-2 p-3 shadow-sm"
    >
      <div class="overflow-x-auto scrollbar-none">
        <div class="flex border border-outline-gray-2 rounded-lg overflow-hidden w-max min-w-full">
          <button
            v-for="hall in halls"
            :key="hall"
            class="flex-1 min-w-[94px] h-10 flex items-center justify-center px-3 border-r border-outline-gray-2 last:border-r-0 text-xs font-semibold uppercase tracking-wide transition-colors shrink-0"
            :class="
              selectedHall === hall
                ? 'bg-surface-gray-3 dark:bg-surface-gray-4 text-ink-gray-9'
                : 'text-ink-gray-5 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'
            "
            @click="$emit('update:selectedHall', hall)"
          >
            {{ hall }}
          </button>
        </div>
      </div>
    </div>

    <div class="p-3">
      <div v-if="sessions.length === 0" class="py-16 text-center text-ink-gray-4 text-sm">
        No sessions scheduled for this hall.
      </div>
      <div v-else class="flex flex-col">
        <SessionCard
          v-for="session in sessions"
          :key="session.name || session.title"
          :session="session"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import SessionCard from '@/components/schedule/SessionCard.vue'

const props = defineProps({
  halls: { type: Array, default: () => [] },
  selectedHall: { type: String, default: '' },
  sessions: { type: Array, default: () => [] },
})

defineEmits(['update:selectedHall'])
</script>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
