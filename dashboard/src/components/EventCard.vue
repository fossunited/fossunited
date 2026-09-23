<template>
  <Card
    :title="event.event_name"
    role="button"
    tabindex="0"
    :aria-label="`Open ${event.event_name} dashboard`"
    class="border-2 border-transparent hover:border-outline-gray-4 transition-colors hover:cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-outline-gray-4"
    @click="goToDashboard"
    @keydown.enter="goToDashboard"
    @keydown.space.prevent="goToDashboard"
  >
    <div class="flex justify-between">
      <div class="text-sm font-medium">
        {{ event.chapter_name }}
      </div>
      <Badge :variant="'subtle'" :theme="badgeColors[event.status]" :label="event.status"></Badge>
    </div>
    <div class="text-sm font-medium">
      {{
        new Date(event.event_start_date).toLocaleDateString('en-IN', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })
      }}
    </div>
  </Card>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const badgeColors = {
  Draft: 'orange',
  Approved: 'green',
  Live: 'green',
  Concluded: 'gray',
  Cancelled: 'red',
}
const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

function goToDashboard() {
  router.push({ name: 'Event Dashboard', params: { id: props.event.name } })
}
</script>
