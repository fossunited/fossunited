<template>
  <div v-if="tickets.data" class="p-4">
    <div class="prose">
      <h2 class="mb-1">My Tickets</h2>
      <p class="text-sm mb-4">All the paid event tickets booked with your account.</p>
    </div>

    <div v-if="tickets.data.length" class="flex flex-col gap-6">
      <div v-if="upcomingTickets.length" class="flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <LivePing />
          <h4 class="text-sm font-medium text-ink-gray-8">Upcoming</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          <span class="w-2 h-2 rounded-full bg-surface-gray-4" />
          <h4 class="text-sm font-medium text-ink-gray-8">Concluded</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TicketCard
            v-for="ticket in concludedTickets"
            :key="ticket.name"
            :ticket="ticket"
            @select="selectedTicket = ticket"
          />
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col gap-2 rounded-sm p-4 border bg-surface-gray-1">
      <div class="text-sm font-medium uppercase text-ink-gray-8">No Tickets</div>
      <div class="text-xs text-ink-gray-5">You haven't booked any event tickets yet.</div>
    </div>
  </div>
  <div v-else class="p-4 text-sm text-ink-gray-5">Loading tickets...</div>

  <Dialog
    :model-value="!!selectedTicket"
    class="z-50"
    :options="{ title: selectedTicket?.event_name }"
    @update:model-value="(val) => !val && (selectedTicket = null)"
  >
    <template #body-content>
      <div v-if="selectedTicket" class="flex flex-col gap-4 text-sm">
        <div class="flex flex-col items-center gap-2">
          <img
            :src="getTicketQrUrl(selectedTicket.name)"
            :alt="`QR code for ticket ${selectedTicket.name}`"
            class="w-48 h-48 object-contain rounded-md bg-surface-gray-1 p-3"
          />
          <p class="text-xs text-ink-gray-5 font-mono">{{ selectedTicket.name }}</p>
          <div class="flex items-center gap-1.5">
            <LivePing v-if="!selectedTicket.is_concluded" />
            <span v-else class="w-2 h-2 rounded-full bg-surface-gray-4" />
            <span class="text-xs text-ink-gray-5">
              {{ selectedTicket.is_concluded ? 'Concluded' : 'Upcoming' }}
            </span>
          </div>
        </div>

        <div
          v-if="selectedTicket.is_transfer_ticket"
          class="text-xs text-ink-blue-4 bg-surface-blue-1 rounded-md px-3 py-2"
        >
          This is a transferred ticket from another person.
        </div>

        <div
          v-if="selectedTicket.is_concluded"
          class="text-xs text-ink-gray-6 bg-surface-gray-2 rounded-md px-3 py-2"
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
              class="text-ink-gray-9 font-medium inline-flex items-center gap-1 hover:underline"
            >
              {{ selectedTicket.event_name }}
              <IconExternalLink
                class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0"
                aria-hidden="true"
              />
            </a>
          </div>
          <div>
            <p class="text-xs text-ink-gray-5">Date</p>
            <button
              type="button"
              class="text-ink-gray-9 inline-flex items-center gap-1 hover:underline disabled:cursor-not-allowed disabled:opacity-60"
              title="Click to add to calendar"
              :disabled="addingToCalendar"
              @click="onAddToCalendarClick"
            >
              <LoadingIndicator
                v-if="addingToCalendar"
                class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0"
              />
              <IconCalendar
                v-else
                class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0"
                aria-hidden="true"
              />
              {{
                getFormattedEventDate(
                  selectedTicket.event_start_date,
                  selectedTicket.event_end_date,
                )
              }}
            </button>
          </div>
          <div v-if="selectedTicket.event_location">
            <p class="text-xs text-ink-gray-5">Venue</p>
            <a
              v-if="selectedTicket.map_link"
              :href="selectedTicket.map_link"
              target="_blank"
              rel="noopener"
              class="text-ink-gray-9 inline-flex items-center gap-1 hover:underline"
            >
              <IconMapPin class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0" aria-hidden="true" />
              {{ selectedTicket.event_location }}
            </a>
            <p v-else class="text-ink-gray-9 inline-flex items-center gap-1">
              <IconMapPin class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0" aria-hidden="true" />
              {{ selectedTicket.event_location }}
            </p>
          </div>
          <div>
            <p class="text-xs text-ink-gray-5">Tier</p>
            <p class="text-ink-gray-9 inline-flex items-center gap-1">
              <IconTicket class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0" aria-hidden="true" />
              {{ selectedTicket.tier }}
            </p>
          </div>
          <div>
            <p class="text-xs text-ink-gray-5">Name</p>
            <p class="text-ink-gray-9 inline-flex items-center gap-1">
              <IconUser class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0" aria-hidden="true" />
              {{ selectedTicket.full_name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-ink-gray-5">Booked on</p>
            <p class="text-ink-gray-9 inline-flex items-center gap-1">
              <IconClock class="w-3.5 h-3.5 text-ink-gray-5 flex-shrink-0" aria-hidden="true" />
              {{ formatCheckinDateTime(selectedTicket.creation) }}
            </p>
          </div>
          <div v-if="selectedTicket.wants_tshirt" class="col-span-2">
            <p class="text-xs text-ink-gray-5">T-shirt</p>
            <span
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border w-fit"
              :class="getTshirtState(selectedTicket).class"
              :title="getTshirtState(selectedTicket).tooltip"
            >
              <IconShirt class="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
              {{ selectedTicket.tshirt_size }}
            </span>
          </div>
        </div>

        <Button
          label="Download ticket"
          variant="solid"
          class="w-full"
          :loading="downloadingTicket"
          @click="onDownloadClick"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { createResource, Dialog, Button, LoadingIndicator } from 'frappe-ui'
import { ref, computed } from 'vue'
import {
  IconShirt,
  IconExternalLink,
  IconCalendar,
  IconClock,
  IconMapPin,
  IconTicket,
  IconUser,
} from '@tabler/icons-vue'
import TicketCard from '@/components/tickets/TicketCard.vue'
import LivePing from '@/components/animation/LivePing.vue'
import { getFormattedEventDate, formatCheckinDateTime } from '@/helpers/date'
import {
  getTicketQrUrl,
  getTicketDownloadUrl,
  getTicketIcsUrl,
  getTicketEventUrl,
  getTshirtState,
} from '@/helpers/tickets'
import { fetchAndDownload } from '@/helpers/utils'
import { useDownloadAction } from '@/composables/useDownloadAction'

const selectedTicket = ref(null)

const tickets = createResource({
  url: 'fossunited.api.tickets.get_session_user_tickets',
  auto: true,
})

const upcomingTickets = computed(() => tickets.data?.filter((t) => !t.is_concluded) ?? [])
const concludedTickets = computed(() => tickets.data?.filter((t) => t.is_concluded) ?? [])

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
