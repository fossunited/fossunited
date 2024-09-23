<template>
  <div v-if="hackathons.data" class="w-full items-center">
    <div class="prose">
      <div class="prose p-4 pb-0">
        <h2 class="mb-1">My Hackathons</h2>
        <p class="text-sm mb-4">
          Keep track of your hackathon entries, view upcoming events, and manage your participation
          details.
        </p>
      </div>
    </div>
    <div v-if="hackathons.data.length > 0" class="p-4 flex flex-col gap-4">
      <div v-if="ongoing_hackathons.length" class="flex flex-col gap-2">
        <div class="prose">
          <h4>Live Hackathons</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card
            v-for="hackathon in ongoing_hackathons"
            :key="hackathon.name"
            :title="hackathon.hackathon_name"
            class="border-2 border-transparent hover:border-gray-500 transition-colors rounded-[8px] hover:cursor-pointer"
            @click="$router.push('/hack/' + hackathon.permalink)"
          />
        </div>
      </div>
      <div v-if="upcoming_hackathons.length" class="flex flex-col gap-2">
        <div class="prose">
          <h4>Upcoming Hackathons</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card
            v-for="hackathon in upcoming_hackathons"
            :key="hackathon.name"
            :title="hackathon.hackathon_name"
            class="border-2 border-transparent hover:border-gray-500 transition-colors rounded-[8px] hover:cursor-pointer"
            @click="$router.push('/hack/' + hackathon.permalink)"
          />
        </div>
      </div>
      <div v-if="past_hackathons.length" class="flex flex-col gap-2">
        <div class="prose">
          <h4>Past Hackathons</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card
            v-for="hackathon in past_hackathons"
            :key="hackathon.name"
            :title="hackathon.hackathon_name"
            class="border-2 border-transparent hover:border-gray-500 transition-colors rounded-[8px] hover:cursor-pointer"
            @click="$router.push('/hack/' + hackathon.permalink)"
          />
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col gap-2 rounded-sm p-4 border bg-gray-50">
      <div class="text-sm font-medium uppercase text-gray-800">No Hackathons</div>
      <div class="text-xs text-gray-600">You have not participated in any hackathons yet.</div>
    </div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

const upcoming_hackathons = ref([])
const past_hackathons = ref([])
const ongoing_hackathons = ref([])

const hackathons = createResource({
  url: 'fossunited.api.hackathon.get_session_user_hackathons',
  auto: true,
  onSuccess(data) {
    const now = new Date()

    data.forEach((hackathon) => {
      const start_date = new Date(hackathon.start_date)
      const end_date = new Date(hackathon.end_date)

      if (end_date < now) {
        past_hackathons.value.push(hackathon)
      } else if (start_date > now) {
        upcoming_hackathons.value.push(hackathon)
      } else {
        ongoing_hackathons.value.push(hackathon)
      }
    })
  },
})
</script>
