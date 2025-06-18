<template>
  <ManageShowcaseDialog
    v-model:show="showDialog"
    v-model:showcase="selectedShowcase"
    :is-new="inAddNew"
    class="z-50"
    @reload:event="event.reload()"
  />
  <div class="flex flex-col gap-4 my-6">
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h2>Project Showcases</h2>
      </div>
      <Button label="Add Showcase" class="w-fit mb-1" @click="handleAddNew" />
      <div v-if="event.doc.project_showcase.length == 0" class="text-sm text-gray-800">
        No showcases added for this event.
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ShowcaseCard
          v-for="showcase in event.doc.project_showcase"
          :key="showcase.name"
          :showcase="showcase"
          @edit:showcase="handleEdit(showcase)"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { inject, reactive, ref } from 'vue'
import ShowcaseCard from '@/components/event/ShowcaseCard.vue'
import ManageShowcaseDialog from '@/components/event/ManageShowcaseDialog.vue'

const inAddNew = ref(false)
let selectedShowcase = reactive({})
const showDialog = ref(false)
const event = inject('event')

const handleAddNew = () => {
  inAddNew.value = true
  selectedShowcase = {}
  showDialog.value = true
}

const handleEdit = (showcase) => {
  inAddNew.value = false
  selectedShowcase = showcase
  showDialog.value = true
}
</script>
