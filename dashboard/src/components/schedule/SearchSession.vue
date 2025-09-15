<template>
  <div class="space-y-4">
    <SessionListHeader
      class="mt-14"
      :title="`Search Results (${filteredSessions.length})`"
      :collapsible="false"
      :view="'vertical'"
    />
    <SessionList :sessions="filteredSessions" :view="'vertical'" />
    <div v-if="filteredSessions.length === 0" class="text-gray-500">
      No sessions found matching "<strong>{{ query }}</strong
      >"
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
      }
    }
  }
  return all
}

const filteredSessions = computed(() => {
  const query = props.query.trim().toLowerCase()
  if (!query) return []

  return flattenSchedule(props.schedule).filter((session) => {
    const title = session.title?.toLowerCase() ?? ''
    const name = session.name?.toLowerCase() ?? ''
    const speakers = (session.cfp_speakers ?? []).map((s) => s.full_name?.toLowerCase()).join(' ')
    return name.includes(query) || title.includes(query) || speakers.includes(query)
  })
})
</script>
