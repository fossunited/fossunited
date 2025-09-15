<template>
  <div class="space-y-4">
    <SessionListHeader
      class="mt-14"
      :title="`Search Results (${filteredSessions.length})`"
      :collapsible="false"
      :view="'vertical'"
    />
    <SessionList :sessions="filteredSessions" :view="'vertical'" />
    <div v-if="filteredSessions.length === 0" class="text-gray-500" aria-live="polite">
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
  for (const day of Object.values(schedule ?? {})) {
    for (const hall of Object.values(day ?? {})) {
      if (Array.isArray(hall)) {
        all.push(...hall)
      } else if (hall && Array.isArray(hall.sessions)) {
        all.push(...hall.sessions)
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
