<template>
  <div v-if="ticket_insights.data" class="flex flex-col gap-6">
    <div class="flex flex-col gap-4">
      <div class="prose">
        <h2 class="mb-1">Insights</h2>
        <p class="text-sm">Get insights about the tickets sold for this event.</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <TicketTierInsightCard :tier="today_stats" />
          <TicketTshirtInsightCard :insight="ticket_insights.data.tshirt_insights" />
      </div>
      <div class="prose mt-4">
        <h4>Tier Insights</h4>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <TicketTierInsightCard
          v-for="tier in ticket_insights.data.tier_data"
          :key="tier.title"
          :tier="tier"
        />
      </div>
    </div>
  </div>
  <div v-else class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>
<script setup>
import { defineProps, reactive } from 'vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { toast } from 'vue-sonner'
import TicketTierInsightCard from '@/components/event/TicketTierInsightCard.vue'
import TicketTshirtInsightCard from '@/components/event/TicketTshirtInsightCard.vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const today_stats = reactive({
  title: 'Total Tickets Sold',
  total_sold: 0,
  tickets_sold_today: 0,
  tier_capacity: false,
})

const ticket_insights = createResource({
  url: 'fossunited.api.tickets.get_tickets_insights',
  makeParams() {
    return {
      event_id: props.event.data.name,
    }
  },
  loading: true,
  auto: true,
  onSuccess(data) {
    today_stats.total_sold = data.total_sold
    today_stats.tickets_sold_today = data.tickets_sold_today
  },
  onError(error) {
    toast.error(error.message)
  },
})
</script>
