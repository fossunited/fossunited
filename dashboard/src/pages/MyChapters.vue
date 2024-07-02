<template>
  <div v-if="chapters.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">My Chapters</h2>
        <p class="text-sm mb-4">Manage the chapters you are a part of.</p>
      </div>
    </div>
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <ChapterCard v-for="chapter in chapters.data" :chapter="chapter" />
    </div>
  </div>
</template>
<script setup>
import { createListResource } from 'frappe-ui'
import { inject } from 'vue'
import ChapterCard from '@/components/ChapterCard.vue'

const session = inject('$session')

const chapters = createListResource({
  doctype: 'FOSS Chapter',
  fields: ['*'],
  filters: [
    ['FOSS Chapter Lead Team Member', 'email', 'like', `%${session.user}%`],
  ],
  auto: true,
  pageLength: 999,
})
</script>
