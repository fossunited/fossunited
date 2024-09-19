<template>
  <ManageTicketTierDialog
    v-model="showDialog"
    :in-create-mode="true"
    @update-tier="event.fetch()"
  />
  <div>
    <div class="prose">
      <h2 class="mb-1">Ticket Tiers</h2>
      <p class="text-sm">Manage the ticket tiers for this event here.</p>
      <Button variant="solid" label="Add Tier" icon-left="plus" @click="showDialog = true" />
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 my-4 gap-4">
      <TicketTierCard
        v-for="tier in event.data.tiers"
        :key="tier.name"
        :tier="tier"
        @update-tier="event.fetch()"
      />
    </div>
  </div>
</template>
<script setup>
import TicketTierCard from '@/components/event/TicketTierCard.vue'
import ManageTicketTierDialog from '@/components/event/ManageTicketTierDialog.vue'
import { defineProps, ref } from 'vue'

const props = defineProps({
  event: {
    type: Object,
    default: null,
  },
})

const showDialog = ref(false)
</script>
