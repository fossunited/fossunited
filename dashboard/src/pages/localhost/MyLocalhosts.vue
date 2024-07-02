<template>
  <div v-if="localhosts.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">My LocalHosts</h2>
        <p class="text-sm mb-4">
            Keep a track of localhosts you organize.
        </p>
      </div>
    </div>
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
            v-for="localhost in localhosts.data"
            :title="localhost.localhost_name"
            class="border-2 border-transparent rounded-[8px] hover:border-gray-500 transition-colors hover:cursor-pointer"
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
