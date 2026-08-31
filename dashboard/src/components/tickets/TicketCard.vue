<template>
  <div
    class="bg-surface-white border border-outline-gray-2 rounded-lg flex items-start hover:border-outline-gray-4 hover:bg-surface-gray-1 transition-colors"
  >
    <button
      type="button"
      class="flex-1 min-w-0 flex gap-4 items-start p-5 text-left rounded-l-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-outline-gray-4"
      @click="$emit('select', ticket)"
    >
      <img
        :src="qrUrl"
        alt=""
        class="w-28 h-28 flex-shrink-0 rounded-md bg-surface-gray-1 p-1.5 object-contain"
      />

      <div class="min-w-0 flex-1 flex flex-col gap-1.5">
        <div class="flex items-center gap-1.5">
          <LivePing v-if="!ticket.is_concluded" />
          <span
            v-else
            class="w-2 h-2 rounded-full bg-surface-gray-4 flex-shrink-0"
            aria-hidden="true"
          />
          <span class="sr-only">{{
            ticket.is_concluded ? 'Concluded event.' : 'Upcoming event.'
          }}</span>
          <p class="text-base font-medium text-ink-gray-9 truncate">{{ ticket.event_name }}</p>
        </div>

        <div class="flex items-center gap-1.5 text-sm text-ink-gray-5 truncate">
          <IconTicket class="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span class="truncate">{{ ticket.tier }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-sm text-ink-gray-5 truncate">
          <IconCalendar class="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span class="truncate">{{
            getFormattedEventDate(ticket.event_start_date, ticket.event_end_date)
          }}</span>
        </div>
        <div
          v-if="ticket.event_location"
          class="flex items-center gap-1.5 text-sm text-ink-gray-5 truncate"
        >
          <IconMapPin class="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span class="truncate">{{ ticket.event_location }}</span>
        </div>
        <span
          v-if="ticket.wants_tshirt"
          class="inline-flex items-center gap-1.5 text-sm px-2 py-0.5 rounded-md border w-fit"
          :class="tshirtState.class"
        >
          <component :is="tshirtState.icon" class="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          {{ ticket.tshirt_size }}
          <span class="sr-only">, {{ tshirtState.tooltip }}</span>
        </span>

        <Badge
          v-if="ticket.is_transfer_ticket"
          class="w-fit"
          variant="subtle"
          theme="blue"
          label="Transferred"
        />
      </div>
    </button>

    <button
      type="button"
      class="w-9 h-9 flex items-center justify-center rounded-md hover:bg-surface-gray-2 transition-colors flex-shrink-0 mt-5 mr-5 disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-outline-gray-4"
      title="Download ticket"
      aria-label="Download ticket"
      :disabled="downloading"
      :aria-busy="downloading"
      @click="onDownloadClick"
    >
      <LoadingIndicator v-if="downloading" class="w-5 h-5 text-ink-gray-6" />
      <IconDownload v-else class="w-5 h-5 text-ink-gray-6" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge, LoadingIndicator } from 'frappe-ui'
import { IconDownload, IconTicket, IconCalendar, IconMapPin } from '@tabler/icons-vue'
import LivePing from '@/components/animation/LivePing.vue'
import { getTicketQrUrl, getTicketDownloadUrl, getTshirtState } from '@/helpers/tickets'
import { getFormattedEventDate } from '@/helpers/date'
import { fetchAndDownload } from '@/helpers/utils'
import { useDownloadAction } from '@/composables/useDownloadAction'

const props = defineProps({
  ticket: { type: Object, required: true },
})
defineEmits(['select'])

const qrUrl = computed(() => getTicketQrUrl(props.ticket.name))
const tshirtState = computed(() => getTshirtState(props.ticket))

const { loading: downloading, run: downloadTicket } = useDownloadAction(
  'Could not download ticket',
)

function onDownloadClick() {
  downloadTicket(() =>
    fetchAndDownload(getTicketDownloadUrl(props.ticket.name), `${props.ticket.name}.pdf`),
  )
}
</script>
