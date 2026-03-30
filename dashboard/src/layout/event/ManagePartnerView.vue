<template>
  <ManagePartnerDialog
    v-model:show="showDialog"
    v-model:partner="selectedPartner"
    :is-new="inAddNew"
    class="z-50"
    @reload:event="event.reload()"
  />
  <div class="flex flex-col gap-4 my-6">
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h2>Community Partners</h2>
      </div>
      <Button label="Add Partner" class="w-fit mb-1" @click="handleAddNew" />
      <div v-if="event.doc.community_partners.length == 0" class="text-sm text-ink-gray-8">
        No partners added for this event.
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <EntityCard
          v-for="partner in event.doc.community_partners"
          :key="partner.name"
          :item="partner"
          image-key="logo"
          name-key="org_name"
          event-field="community_partners"
          label="Partner"
          @edit="handleEdit(partner)"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { inject, reactive, ref } from 'vue'
import EntityCard from '@/components/event/EntityCard.vue'
import ManagePartnerDialog from '@/components/event/ManagePartnerDialog.vue'

const inAddNew = ref(false)
let selectedPartner = reactive({})
const showDialog = ref(false)
const event = inject('event')

const handleAddNew = () => {
  inAddNew.value = true
  selectedPartner = {}
  showDialog.value = true
}

const handleEdit = (partner) => {
  inAddNew.value = false
  selectedPartner = partner
  showDialog.value = true
}
</script>
