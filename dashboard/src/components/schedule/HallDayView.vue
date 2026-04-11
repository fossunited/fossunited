<template>
  <div
    class="w-full mt-3 bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-xl overflow-hidden"
  >
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

defineProps({
  sessions: { type: Array, default: () => [] },
})
</script>
