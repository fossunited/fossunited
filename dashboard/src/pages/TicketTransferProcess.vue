<template>
  <Dialog
    class="z-50"
    v-model="showDialog"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
  />
  <Header />
  <div class="w-full h-screen flex justify-center">
    <div
      v-if="transferDoc.data && transferStatus"
      class="max-w-screen-xl w-full flex justify-center"
    >
      <StatusMessage :status="transferStatus" />
    </div>
    <div v-else class="flex w-full justify-center items-center">
      <LoadingIndicator class="w-6" />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import { createResource, Dialog, usePageMeta, LoadingIndicator } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import StatusMessage from '@/components/ticket_transfer/StatusMessage.vue'

const route = useRoute()

usePageMeta(() => {
  return {
    title: 'Ticket Transfer',
  }
})

const transferStatus = ref('')

const ticket = route.query.ticket
const transferID = route.query.id
const toApprove = route.query.status

const showDialog = ref(false)
const dialogTitle = ref('Error')
const dialogMessage = ref('')

const ticketDoc = createResource({
  url: 'fossunited.api.tickets.get_ticket_details',
  makeParams() {
    return {
      ticket_id: ticket,
    }
  },
})

onMounted(() => {
  if (!isValidStatus()) {
    return
  }
  validateTicket.fetch()
  validateTransferId.fetch()
})

const isValidStatus = () => {
  if (toApprove == null || toApprove == undefined || (toApprove != 1 && toApprove != 0)) {
    dialogMessage.value += 'Invalid URL. Please contact system admin.'
    showDialog.value = true
    return false
  }
  return true
}

const validateTicket = createResource({
  url: 'fossunited.api.tickets.check_ticket_validity',
  params: {
    ticket_id: ticket,
  },
  onSuccess(data) {
    if (!data) {
      showDialog.value = true
      dialogMessage.value += ' The ticket you are trying to transfer does not exist.'
    } else {
      ticketDoc.fetch()
    }
  },
})

const transferDoc = createResource({
  url: 'fossunited.api.tickets.get_transfer_details',
  makeParams() {
    return {
      id: transferID,
    }
  },
  loading: true,
  onSuccess(data) {
    if (data.status == 'Pending Approval') {
      if (toApprove == 1) {
        approveTransfer(data)
      } else {
        rejectTransfer(data)
      }
    } else if (data.status == 'Completed') {
      transferStatus.value = 'Already Approved'
    } else if (data.status == 'Cancelled') {
      transferStatus.value = 'Already Rejected'
    }
  },
})

const approveTransfer = (data) => {
  createResource({
    url: 'fossunited.api.tickets.change_transfer_status',
    makeParams() {
      return {
        transfer_id: data.name,
        status: 'Completed',
      }
    },
    auto: true,
    onSuccess(data) {
      transferStatus.value = 'Approved'
    },
    onError(err) {
      console.log(err)
      dialogMessage.value +=
        ' There was an error while approving the transfer request. Please contact system admin.' +
        err
      showDialog.value = true
    },
  })
}

const rejectTransfer = (data) => {
  createResource({
    url: 'fossunited.api.tickets.change_transfer_status',
    params: {
      transfer_id: data.name,
      status: 'Cancelled',
    },
    auto: true,
    onSuccess(data) {
      transferStatus.value = 'Rejected'
    },
    onError(err) {
      console.log(err)
      dialogMessage.value +=
        ' There was an error while rejecting the transfer request. Please contact system admin.' +
        err
      showDialog.value = true
    },
  })
}

const validateTransferId = createResource({
  url: 'fossunited.api.tickets.get_transfer_doc_validity',
  params: {
    transfer_id: transferID,
  },
  onSuccess(data) {
    if (!data) {
      showDialog.value = true
      dialogMessage.value += ' The transfer request you are trying to approve does not exist. '
      return false
    } else {
      transferDoc.fetch()
    }
  },
})
</script>
