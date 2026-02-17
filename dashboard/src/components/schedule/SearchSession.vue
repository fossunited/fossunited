<template>
  <div class="space-y-4">
    <SessionListHeader
      class="mt-14"
      :title="`Search Results (${filteredSessions.length})`"
      :collapsible="false"
      :view="'vertical'"
    />
    <SessionList :sessions="filteredSessions" :view="'vertical'" />
    <div v-if="filteredSessions.length === 0" class="text-ink-gray-4" aria-live="polite">
      No sessions found matching <strong>{{ query }}</strong
      >.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SessionList from '@/components/schedule/SessionList.vue'
import SessionListHeader from '@/components/schedule/SessionListHeader.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true, // all dates
  },
  query: {
    type: String,
    required: true,
  },
})

// Flatten and filter all sessions
function flattenSchedule(schedule) {
  const all = []
  for (const [date, day] of Object.entries(schedule ?? {})) {
    for (const [hallName, hall] of Object.entries(day ?? {})) {
      const sessions = Array.isArray(hall)
        ? hall
        : hall && Array.isArray(hall.sessions)
          ? hall.sessions
          : []

      for (const session of sessions) {
        all.push({
          ...session,
          _date: date,
          _hall: hallName,
        })
      }
    }
  }
  return all
}

const allSessions = computed(() => flattenSchedule(props.schedule))
const filteredSessions = computed(() => {
  const query = props.query.trim().toLowerCase()
  if (!query) return []

  return allSessions.value.filter((session) => {
    const parts = [
      session.name,
      session.title,
      session.category,
      ...(session.cfp_speakers ?? []).flatMap((s) => [s.full_name, s.designation, s.organization]),
    ]
      .filter(Boolean)
      .map((s) => String(s).toLowerCase())
    const haystack = parts.join(' ')
    return haystack.includes(query)
  })
})
</script>
