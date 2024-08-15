<template>
  <div v-if="event.data" class="w-full z-0 px-4 py-4 md:p-8">
    <EventHeader :event="event.doc" v-if="event.doc" />
    <hr class="my-5" />

    <div class="flex flex-col gap-4">
      <!-- Manage Tickets -->
      <div>
        <div class="prose w-full">
          <h2 class="mb-1">Manage Tickets</h2>
          <p class="text-sm">You can manage the tickets for this event here.</p>
        </div>
        <div
          class="w-full md:w-1/3 mt-4 flex gap-2 flex-col p-4 border rounded-sm border-gray-500 border-dashed"
        >
          <div>
            <div class="text-base font-semibold mb-1">
              Tickets are
              <span
                :class="
                  { Live: 'text-green-700', Closed: 'text-red-600' }[
                    event.data.tickets_status
                  ]
                "
                >{{ event.data.tickets_status }}</span
              >
            </div>
            <p class="text-sm text-gray-600">
              {{ ticketSubtitle[event.data.tickets_status] }}
            </p>
          </div>
          <Button
            class="w-fit mt-2"
            :label="
              { Live: 'Deactivate', Closed: 'Activate' }[
                event.data.tickets_status
              ]
            "
            :theme="{ Live: 'red', Closed: 'gray' }[event.data.tickets_status]"
            @click="toggleTicketStatus.fetch()"
          />
        </div>
      </div>

      <!-- Ticket Tier Section -->
      <TicketTierSection :event="event"/>

      <!-- Tshirt Section -->
      <TicketTshirtSection :event="event"/>

      <!-- Custom Fields -->
      <TicketCustomFieldsSection :event="event" />
    </div>
  </div>
  <div v-else class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import TicketTierSection from '@/components/event/TicketTierSection.vue'
import TicketTshirtSection from '@/components/event/TicketTshirtSection.vue'
import TicketCustomFieldsSection from '@/components/event/TicketCustomFieldsSection.vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()

const ticketSubtitle = {
  Live: 'Tickets are currently available for purchase.',
  Closed: 'Tickets are currently not available for purchase.',
}

const event = createResource({
  url: 'frappe.client.get',
  makeParams(){
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fields: ['*'],
    }
  },
  onSuccess(data){
    event.doc = data
  },
  auto: true,
})

const toggleTicketStatus = createResource({
  url: 'frappe.client.set_value',
  makeParams(){
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fieldname: 'tickets_status',
      value: event.data.tickets_status === 'Live' ? 'Closed' : 'Live',
    }
  },
  onSuccess(){
    event.fetch()
  }
})


</script>
