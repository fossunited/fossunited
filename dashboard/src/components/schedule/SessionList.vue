<template>
  <div
    class="py-6 border-l border-gray-500 flex flex-col gap-6"
    :class="{
      'h-full': view === 'horizontal',
    }"
  >
    <div v-for="session in sessions" class="flex items-center">
      <div
        class="relative flex items-center justify-center"
        :class="{
          'w-1/12 md:w-1/5': view === 'vertical',
          'md:w-2/6': view === 'horizontal',
        }"
      >
        <div class="absolute inset-0 flex items-center">
          <div class="w-full h-px bg-gray-500"></div>
        </div>
        <SessionTimeComponent
          :session="session"
          class="z-20 mx-5 invisible md:visible shrink-0"
        />
      </div>
      <div
        class="relative flex flex-col items-start"
        :class="{
          'w-full md:w-4/5': view === 'vertical',
          'w-4/6': view === 'horizontal',
        }"
      >
        <SessionTimeComponent
          :session="session"
          :class="{
            'md:hidden z-20 mx-4 -mb-9': view === 'vertical',
            hidden: view === 'horizontal',
          }"
        />
        <SessionCard :session="session" />
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
  view: {
    type: String,
    required: true,
    default: 'vertical',
  },
})
</script>
