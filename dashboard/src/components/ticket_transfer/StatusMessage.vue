<template>
  <div class="py-10 px-5 w-full flex justify-center">
    <div v-if="isApprovedStatus" class="flex flex-col items-center gap-2 text-center max-w-md">
      <IconCircleCheckFilled class="w-10 h-10 fill-green-600 shrink-0" />
      <div class="prose text-center">
        <div v-if="status === 'Approved'">
          <h2 class="my-3">Ticket Transferred Successfully!</h2>
          <p>
            The ticket has been successfully transferred to the new owner.<br />
            An email has been sent to the new ticket holder.
          </p>
        </div>
        <div v-else>
          <h2 class="my-3">Ticket Already Transferred!</h2>
          <p>
            This ticket has already been transferred to the new owner.<br />
            An email was sent to the new ticket holder.
          </p>
        </div>
      </div>
    </div>

    <div
      v-else-if="isRejectedStatus"
      class="flex flex-col text-center items-center gap-2 max-w-md"
    >
      <IconCircleXFilled class="w-10 h-10 fill-red-600 shrink-0" />
      <div class="prose text-center">
        <div v-if="status === 'Rejected'">
          <h2 class="my-3">Transfer Rejected</h2>
          <p>
            The ticket transfer request has been rejected. The ticket stays with the original
            owner.
          </p>
        </div>
        <div v-else>
          <h2 class="my-3">Transfer Already Rejected</h2>
          <p>This ticket transfer request has already been rejected.</p>
        </div>
      </div>
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>

    <div
      v-else-if="status === 'LoginRequired'"
      class="flex flex-col text-center items-center gap-3 max-w-md"
    >
      <IconLogin2 class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Login Required</h2>
        <p>{{ message || 'Please log in with your FOSS United account to continue.' }}</p>
      </div>
      <Button variant="solid" theme="green" label="Continue to Login" @click="$emit('login')" />
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>

    <div
      v-else-if="status === 'NotAuthorized'"
      class="flex flex-col text-center items-center gap-2 max-w-md"
    >
      <IconLock class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Not Authorized</h2>
        <p>{{ message || 'You are not authorized to perform this action.' }}</p>
      </div>
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>

    <div
      v-else-if="status === 'RateLimited'"
      class="flex flex-col text-center items-center gap-2 max-w-md"
    >
      <IconClock class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Too Many Attempts</h2>
        <p>{{ message || "You've made too many attempts. Please wait a while and try again." }}</p>
      </div>
    </div>

    <div
      v-else-if="status === 'NotFound'"
      class="flex flex-col text-center items-center gap-2 max-w-md"
    >
      <IconAlertTriangle class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Transfer Not Found</h2>
        <p>
          {{ message || "We couldn't find this transfer request. The link may be incorrect." }}
        </p>
      </div>
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>

    <div
      v-else-if="status === 'InvalidUrl'"
      class="flex flex-col text-center items-center gap-2 max-w-md"
    >
      <IconAlertTriangle class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Invalid Link</h2>
        <p>
          {{
            message ||
            'This link looks incomplete or broken. Please use the Approve/Reject link from your email.'
          }}
        </p>
      </div>
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>

    <div v-else class="flex flex-col text-center items-center gap-2 max-w-md">
      <IconAlertTriangle class="w-10 h-10 text-ink-gray-6 shrink-0" />
      <div class="prose text-center">
        <h2 class="my-3">Something Went Wrong</h2>
        <p>{{ message || 'Please try again in a bit.' }}</p>
      </div>
      <p v-if="contactEmail" class="text-sm text-ink-gray-5">
        Need help? Email
        <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a
        >.
      </p>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { Button } from 'frappe-ui'
import {
  IconCircleCheckFilled,
  IconCircleXFilled,
  IconLogin2,
  IconLock,
  IconClock,
  IconAlertTriangle,
} from '@tabler/icons-vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
  // Specific text for the current failure (usually the server's own message);
  // each state falls back to sensible default copy when this is empty.
  message: {
    type: String,
    default: '',
  },
  contactEmail: {
    type: String,
    default: 'developers@fossunited.org',
  },
})

defineEmits(['login'])

const isApprovedStatus = computed(
  () => props.status === 'Approved' || props.status === 'AlreadyApproved',
)
const isRejectedStatus = computed(
  () => props.status === 'Rejected' || props.status === 'AlreadyRejected',
)
</script>
