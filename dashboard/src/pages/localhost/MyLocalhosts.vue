<template>
  <div v-if="localhosts.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">My LocalHosts</h2>
        <p class="text-sm mb-4">
          Keep track of your hackathon entries, view upcoming events, and manage
          your participation details.
        </p>
      </div>
    </div>
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
            v-for="localhost in localhosts.data"
            :title="localhost.localhost_name"
            class="hover:cursor-pointer shadow-none rounded-[8px] hover:border-gray-400 transition-colors"
            @click="$router.push('/localhost/' + localhost.name)"
        />
    </div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'

const localhosts = createResource({
  url: 'fossunited.api.hackathon.get_user_localhosts',
  auto: true,
})
</script>
