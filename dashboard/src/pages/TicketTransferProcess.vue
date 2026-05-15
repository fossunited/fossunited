<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
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
import { showError } from '@/helpers/utils'

const route = useRoute()

usePageMeta(() => {
  return {
    title: 'Ticket Transfer',
  }
})

const transferStatus = ref('')

const transferID = route.query.id
const toApprove = route.query.status

const showDialog = ref(false)
const dialogMessage = ref('')

onMounted(() => {
  if (!isValidStatus()) {
    return
  }
  transferDoc.fetch()
})

const isValidStatus = () => {
  if (toApprove == null || toApprove == undefined || (toApprove != 1 && toApprove != 0)) {
    dialogMessage.value += 'Invalid URL. Please contact system admin.'
    showDialog.value = true
    return false
  }
  return true
}

const transferDoc = createResource({
  url: 'fossunited.api.tickets.get_transfer_details',
  makeParams() {
    return {
      id: transferID,
    }
  },
  loading: true,
  onSuccess(data) {
    if (!data) {
      dialogMessage.value = 'The transfer request does not exist.'
      showDialog.value = true
      return
    }
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
  onError(err) {
    showError(err, 'Failed to fetch transfer details')
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
      if (err?.response?.status === 401 || err?.status === 401) {
        window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname + window.location.search)}`
        return
      }
      showError(err, 'There was an error while approving the transfer request')
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
      if (err?.response?.status === 401 || err?.status === 401) {
        window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname + window.location.search)}`
        return
      }
      showError(err, 'There was an error while rejecting the transfer request')
    },
  })
}

</script>
