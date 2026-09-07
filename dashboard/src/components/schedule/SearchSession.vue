<template>
  <div class="mt-4">
    <div class="flex items-center gap-2 mb-4">
      <span class="text-sm font-semibold text-ink-gray-7 dark:text-ink-gray-8 uppercase tracking-wide">
        {{ label }}
      </span>
      <span
        class="px-2 py-0.5 rounded-full bg-surface-gray-2 text-ink-gray-7 dark:text-ink-gray-8 text-xs font-semibold"
      >
        {{ filteredSessions.length }}
      </span>
    </div>

    <div
      v-if="filteredSessions.length === 0"
      class="py-16 text-center text-ink-gray-7 dark:text-ink-gray-8"
    >
      <template v-if="filter">{{ emptyText }}</template>
      <template v-else>
        No sessions found matching
        <strong class="text-ink-gray-7 dark:text-ink-gray-8">{{ query }}</strong>.
      </template>
    </div>

    <div v-else class="flex flex-col gap-1">
      <SessionCard
        v-for="session in filteredSessions"
        :key="session.name || session.title"
        :session="session"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SessionCard from '@/components/schedule/SessionCard.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true, // all dates
  },
  query: {
    type: String,
    default: '',
  },
  // When given, replaces the query search entirely.
  filter: {
    type: Function,
    default: null,
  },
  label: {
    type: String,
    default: 'Search results',
  },
  emptyText: {
    type: String,
    default: '',
  },
})

function flattenSchedule(schedule) {
  const all = []
  for (const [date, day] of Object.entries(schedule ?? {})) {
    for (const [hallName, sessions] of Object.entries(day ?? {})) {
      const list = Array.isArray(sessions) ? sessions : []
      for (const session of list) {
        all.push({ ...session, _date: date, _hall: hallName })
      }
    }
  }
  return all
}

const allSessions = computed(() => flattenSchedule(props.schedule))

const filteredSessions = computed(() => {
  if (props.filter) return allSessions.value.filter(props.filter)

  const q = props.query.trim().toLowerCase()
  if (!q) return []

  return allSessions.value.filter((session) => {
    const speakers = session.cfp_speakers ?? []
    const parts = [
      session.name,
      session.title,
      session.category,
      session.other_category,
      session.hall,
      ...speakers.flatMap((s) => [s.full_name, s.designation, s.organization]),
    ]
      .filter(Boolean)
      .map((s) => String(s).toLowerCase())
    return parts.join(' ').includes(q)
  })
})
</script>
