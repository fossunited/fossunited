<template>
  <div v-if="tickets.data" class="p-4">
    <div class="prose">
      <h2 class="mb-1">My Tickets</h2>
      <p class="mb-4 text-sm">All the paid event tickets booked with your account.</p>
    </div>

    <div v-if="tickets.data.length" class="flex flex-col gap-6">
      <div v-if="upcomingTickets.length" class="flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <LivePing />
          <h3 class="text-sm-medium text-ink-gray-8">Upcoming</h3>
        </div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <TicketCard
            v-for="ticket in upcomingTickets"
            :key="ticket.name"
            :ticket="ticket"
            @select="selectedTicket = ticket"
          />
        </div>
      </div>

      <div v-if="concludedTickets.length" class="flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-surface-gray-4" aria-hidden="true" />
          <h3 class="text-sm-medium text-ink-gray-8">Concluded</h3>
        </div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <TicketCard
            v-for="ticket in concludedTickets"
            :key="ticket.name"
            :ticket="ticket"
            @select="selectedTicket = ticket"
          />
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col gap-2 rounded-1 border bg-surface-gray-1 p-4">
      <div class="text-sm-medium uppercase text-ink-gray-8">No Tickets</div>
      <div class="text-xs text-ink-gray-5">You haven't booked any event tickets yet.</div>
    </div>
  </div>
  <div v-else class="p-4 text-sm text-ink-gray-5">Loading tickets...</div>

  <Dialog
    :open="!!selectedTicket"
    class="z-50"
    :title="selectedTicket?.event_name"
    @update:open="(val) => !val && (selectedTicket = null)"
  >
    <div v-if="selectedTicket" class="flex flex-col gap-4 text-sm">
      <div class="flex flex-col items-center gap-2">
        <img
          :src="getTicketQrUrl(selectedTicket.name)"
          :alt="`QR code for ticket ${selectedTicket.name}`"
          class="h-48 w-48 rounded-5 bg-surface-gray-1 object-contain p-3"
        />
        <p class="font-mono text-xs text-ink-gray-5">{{ selectedTicket.name }}</p>
        <div class="flex items-center gap-1.5">
          <LivePing v-if="!selectedTicket.is_concluded" />
          <span v-else class="h-2 w-2 rounded-full bg-surface-gray-4" aria-hidden="true" />
          <span class="text-xs text-ink-gray-5">
            {{ selectedTicket.is_concluded ? 'Concluded' : 'Upcoming' }}
          </span>
        </div>
      </div>

      <div
        v-if="selectedTicket.is_transfer_ticket"
        class="rounded-5 bg-surface-blue-1 px-3 py-2 text-xs text-ink-blue-8"
      >
        This is a transferred ticket from another person.
      </div>

      <div
        v-if="selectedTicket.is_concluded"
        class="rounded-5 bg-surface-gray-2 px-3 py-2 text-xs text-ink-gray-6"
      >
        This event has concluded. Check the event page for photos, recordings, and more.
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xs text-ink-gray-5">Event</p>
          <a
            :href="getTicketEventUrl(selectedTicket)"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1 font-medium text-ink-gray-9 hover:underline"
          >
            {{ selectedTicket.event_name }}
            <IconExternalLink
              class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5"
              aria-hidden="true"
            />
          </a>
        </div>
        <div>
          <p class="text-xs text-ink-gray-5">Date</p>
          <button
            type="button"
            class="inline-flex items-center gap-1 text-ink-gray-9 hover:underline disabled:cursor-not-allowed disabled:opacity-60"
            title="Click to add to calendar"
            :disabled="addingToCalendar"
            :aria-busy="addingToCalendar"
            @click="onAddToCalendarClick"
          >
            <LoadingIndicator
              v-if="addingToCalendar"
              class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5"
            />
            <IconCalendar
              v-else
              class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5"
              aria-hidden="true"
            />
            <span class="sr-only">Add </span>
            {{
              getFormattedEventDate(selectedTicket.event_start_date, selectedTicket.event_end_date)
            }}
            <span class="sr-only"> to your calendar</span>
          </button>
        </div>
        <div v-if="selectedTicket.event_location">
          <p class="text-xs text-ink-gray-5">Venue</p>
          <a
            v-if="selectedTicket.map_link"
            :href="selectedTicket.map_link"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1 text-ink-gray-9 hover:underline"
          >
            <IconMapPin class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5" aria-hidden="true" />
            {{ selectedTicket.event_location }}
          </a>
          <p v-else class="inline-flex items-center gap-1 text-ink-gray-9">
            <IconMapPin class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5" aria-hidden="true" />
            {{ selectedTicket.event_location }}
          </p>
        </div>
        <div>
          <p class="text-xs text-ink-gray-5">Tier</p>
          <p class="inline-flex items-center gap-1 text-ink-gray-9">
            <IconTicket class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5" aria-hidden="true" />
            {{ selectedTicket.tier }}
          </p>
        </div>
        <div>
          <p class="text-xs text-ink-gray-5">Name</p>
          <p class="inline-flex items-center gap-1 text-ink-gray-9">
            <IconUser class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5" aria-hidden="true" />
            {{ selectedTicket.full_name }}
          </p>
        </div>
        <div>
          <p class="text-xs text-ink-gray-5">Booked on</p>
          <p class="inline-flex items-center gap-1 text-ink-gray-9">
            <IconClock class="h-3.5 w-3.5 flex-shrink-0 text-ink-gray-5" aria-hidden="true" />
            {{ formatCheckinDateTime(selectedTicket.creation) }}
          </p>
        </div>
        <div v-if="selectedTicket.wants_tshirt" class="col-span-2">
          <p class="text-xs text-ink-gray-5">T-shirt</p>
          <span
            class="inline-flex w-fit items-center gap-1 rounded-5 border px-2 py-0.5"
            :class="selectedTshirtState.class"
            :title="selectedTshirtState.tooltip"
          >
            <component
              :is="selectedTshirtState.icon"
              class="h-3.5 w-3.5 flex-shrink-0"
              aria-hidden="true"
            />
            {{ selectedTicket.tshirt_size }}
            <span class="sr-only">, {{ selectedTshirtState.tooltip }}</span>
          </span>
        </div>
      </div>

      <Button
        label="Download ticket"
        variant="solid"
        class="w-full"
        :loading="downloadingTicket"
        :aria-busy="downloadingTicket"
        @click="onDownloadClick"
      />
    </div>
  </Dialog>
</template>

<script setup>
import {
  IconExternalLink,
  IconCalendar,
  IconClock,
  IconMapPin,
  IconTicket,
  IconUser,
} from '@tabler/icons-vue'
import { createResource, Dialog, Button, LoadingIndicator } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

import LivePing from '@/components/animation/LivePing.vue'
import TicketCard from '@/components/tickets/TicketCard.vue'
import { useDownloadAction } from '@/composables/useDownloadAction'
import { getFormattedEventDate, formatCheckinDateTime } from '@/helpers/date'
import {
  getTicketQrUrl,
  getTicketDownloadUrl,
  getTicketIcsUrl,
  getTicketEventUrl,
  getTshirtState,
} from '@/helpers/tickets'
import { fetchAndDownload } from '@/helpers/utils'

const route = useRoute()
const router = useRouter()
const selectedTicket = ref(null)

const tickets = createResource({
  url: 'fossunited.api.tickets.get_session_user_tickets',
  auto: true,
  onSuccess: openTicketFromQuery,
})

// The printed ticket's QR links to /my-tickets?id=<ticket>; open that ticket's dialog.
function openTicketFromQuery(data) {
  const id = route.query.id
  if (!id) return
  const ticket = data.find((t) => t.name === id)
  if (ticket) {
    selectedTicket.value = ticket
  } else {
    toast.error('This ticket is not in your account.')
    router.replace({ query: { ...route.query, id: undefined } })
  }
}

// Keep ?id= in step with the open dialog, so a refresh or a shared link lands on it.
watch(selectedTicket, (ticket) => {
  const id = ticket?.name
  if (route.query.id === id) return
  router.replace({ query: { ...route.query, id } })
})

const upcomingTickets = computed(() => tickets.data?.filter((t) => !t.is_concluded) ?? [])
const concludedTickets = computed(() => tickets.data?.filter((t) => t.is_concluded) ?? [])
const selectedTshirtState = computed(
  () => selectedTicket.value && getTshirtState(selectedTicket.value),
)

const { loading: downloadingTicket, run: downloadTicket } = useDownloadAction(
  'Could not download ticket',
)
const { loading: addingToCalendar, run: addToCalendar } = useDownloadAction(
  'Could not add to calendar',
)

function onDownloadClick() {
  downloadTicket(() =>
    fetchAndDownload(
      getTicketDownloadUrl(selectedTicket.value.name),
      `${selectedTicket.value.name}.pdf`,
    ),
  )
}

function onAddToCalendarClick() {
  addToCalendar(() =>
    fetchAndDownload(
      getTicketIcsUrl(selectedTicket.value.event),
      `${selectedTicket.value.event}.ics`,
    ),
  )
}
</script>
