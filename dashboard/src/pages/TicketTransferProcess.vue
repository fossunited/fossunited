<template>
  <Header />
  <div class="w-full min-h-[80vh] flex justify-center items-center px-4 py-10">
    <div v-if="phase === 'loading'" class="flex w-full justify-center items-center">
      <LoadingIndicator class="w-6" />
    </div>
    <TransferConfirmation
      v-else-if="phase === 'confirm'"
      :action="action"
      :event-name="transferInfo.eventName"
      :ticket-tier="transferInfo.ticketTier"
      :receiver-name="transferInfo.receiverName"
      :receiver-email="transferInfo.receiverEmail"
      :loading="changeStatus.loading"
      @confirm="handleConfirm"
    />
    <StatusMessage
      v-else
      :status="doneStatus"
      :message="doneMessage"
      :contact-email="contactEmail"
      @login="goToLogin"
    />
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import { createResource, usePageMeta, LoadingIndicator } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import StatusMessage from '@/components/ticket_transfer/StatusMessage.vue'
import TransferConfirmation from '@/components/ticket_transfer/TransferConfirmation.vue'
import { getFriendlyError } from '@/helpers/utils'

const route = useRoute()

usePageMeta(() => {
  return {
    title: 'Ticket Transfer',
  }
})

const transferID = route.query.id
const toApprove = route.query.status
const token = route.query.token || ''
const action = computed(() => (toApprove == 1 ? 'approve' : 'reject'))

// 'loading' -> 'confirm' -> 'done', or straight to 'done' on any error/invalid link
const phase = ref('loading')
const doneStatus = ref('')
const doneMessage = ref('')
const contactEmail = ref('developers@fossunited.org')
const transferInfo = ref({})

const KIND_TO_STATUS = {
  'rate-limit': 'RateLimited',
  auth: 'LoginRequired',
  permission: 'NotAuthorized',
  'not-found': 'NotFound',
}

function showError(err) {
  const { kind, message } = getFriendlyError(err)
  phase.value = 'done'
  doneStatus.value = KIND_TO_STATUS[kind] || 'Error'
  doneMessage.value = message
}

function isValidQuery() {
  return Boolean(transferID) && (toApprove == 1 || toApprove == 0)
}

onMounted(() => {
  if (!isValidQuery()) {
    phase.value = 'done'
    doneStatus.value = 'InvalidUrl'
    return
  }
  transferDoc.fetch()
})

const transferDoc = createResource({
  url: 'fossunited.api.tickets.get_transfer_details',
  method: 'GET',
  makeParams() {
    return {
      id: transferID,
      token,
    }
  },
  onSuccess(data) {
    if (!data) {
      phase.value = 'done'
      doneStatus.value = 'NotFound'
      return
    }
    contactEmail.value = data.contact_email || contactEmail.value

    if (data.status === 'Completed') {
      phase.value = 'done'
      doneStatus.value = 'AlreadyApproved'
      return
    }
    if (data.status === 'Cancelled') {
      phase.value = 'done'
      doneStatus.value = 'AlreadyRejected'
      return
    }

    transferInfo.value = {
      eventName: data.event_name,
      ticketTier: data.ticket_tier,
      receiverName: data.receiver_name,
      receiverEmail: data.receiver_email,
    }
    phase.value = 'confirm'
  },
  onError: showError,
})

const changeStatus = createResource({
  url: 'fossunited.api.tickets.change_transfer_status',
  makeParams() {
    return {
      transfer_id: transferID,
      status: toApprove == 1 ? 'Completed' : 'Cancelled',
      token,
    }
  },
  onSuccess() {
    phase.value = 'done'
    doneStatus.value = toApprove == 1 ? 'Approved' : 'Rejected'
  },
  onError: showError,
})

function handleConfirm() {
  changeStatus.fetch()
}

function goToLogin() {
  // Reconstructed from just id+status - dropping `token` on purpose: this
  // path only fires when the token already failed to verify (or was never
  // present), so it's not needed post-login, and there's no reason to carry
  // it through an extra URL param (login-page logs, browser history, etc).
  const target = `${window.location.pathname}?${new URLSearchParams({ id: transferID, status: toApprove }).toString()}`
  window.location.href = `/login?redirect-to=${encodeURIComponent(target)}`
}
</script>
