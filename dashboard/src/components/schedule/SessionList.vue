<template>
  <div class="py-6 border-l border-gray-500 flex flex-col gap-6">
    <div v-for="session in sessions" class="flex items-center">
      <div class="relative w-1/12 md:w-1/5 flex items-center justify-center">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full h-px bg-gray-500"></div>
        </div>
        <SessionTimeComponent
          :session="session"
          class="z-20 mx-5 invisible md:visible"
        />
      </div>
      <div class="relative flex flex-col items-start w-full md:w-4/5">
        <SessionTimeComponent :session="session" class="md:hidden z-20 mx-4 -mb-9" />
        <SessionCard :session="session"/>
      </div>
    </div>
  </div>
</template>
<script setup>
import SessionTimeComponent from '@/components/schedule/SessionTimeComponent.vue'
import SessionCard from '@/components/schedule/SessionCard.vue'
import { defineProps } from 'vue'

const props = defineProps({
  sessions: {
    type: Array,
    required: true,
  },
})
</script>
