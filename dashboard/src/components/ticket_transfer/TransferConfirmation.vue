<template>
  <div
    class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 md:p-8 flex flex-col gap-5 max-w-md w-full"
  >
    <div class="prose">
      <h2 class="my-0">
        {{ action === 'approve' ? 'Approve Ticket Transfer' : 'Reject Ticket Transfer' }}
      </h2>
    </div>

    <div class="flex flex-col gap-2 text-sm">
      <div v-if="eventName" class="flex justify-between gap-4">
        <span class="text-ink-gray-5">Event</span>
        <span class="text-ink-gray-9 font-medium text-right">{{ eventName }}</span>
      </div>
      <div v-if="ticketTier" class="flex justify-between gap-4">
        <span class="text-ink-gray-5">Ticket Tier</span>
        <span class="text-ink-gray-9 font-medium text-right">{{ ticketTier }}</span>
      </div>
      <div class="flex justify-between gap-4">
        <span class="text-ink-gray-5">Transferring to</span>
        <span class="text-ink-gray-9 font-medium text-right">
          {{ receiverName }}<br />
          <span class="text-ink-gray-5 font-normal">{{ receiverEmail }}</span>
        </span>
      </div>
    </div>

    <p class="text-sm text-ink-gray-6">
      <template v-if="action === 'approve'">
        Approving will transfer this ticket to the recipient above. This cannot be undone.
      </template>
      <template v-else>
        Rejecting will cancel this transfer request. You'll keep your ticket.
      </template>
    </p>

    <Button
      class="w-full font-medium"
      :label="action === 'approve' ? 'Approve Transfer' : 'Reject Transfer'"
      variant="solid"
      :theme="action === 'approve' ? 'green' : 'red'"
      size="md"
      :loading="loading"
      @click="$emit('confirm')"
    />
  </div>
</template>
<script setup>
import { Button } from 'frappe-ui'

defineProps({
  action: { type: String, required: true }, // 'approve' | 'reject'
  eventName: { type: String, default: '' },
  ticketTier: { type: String, default: '' },
  receiverName: { type: String, default: '' },
  receiverEmail: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['confirm'])
</script>
