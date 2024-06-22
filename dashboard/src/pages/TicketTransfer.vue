<template>
  <Header />
  <div class="w-full flex items-center justify-center">
    <TransferSuccess v-if="inSuccess" />
    <div v-else class="max-w-screen-xl w-full p-5">
      <div class="mt-8">
        <div class="prose">
          <div class="text-base uppercase font-medium text-gray-600 mb-2">
            Portal
          </div>
          <h1 class="m-0">Ticket Transfers</h1>
          <div
            v-if="transfer_settings.doc"
            v-html="transfer_settings.doc.web_page_description"
          ></div>
        </div>
      </div>
      <div class="bg-white p-6 rounded border w-full">
        <div class="flex flex-col md:grid md:grid-cols-2 gap-4">
          <div class="col-span-2 flex flex-col gap-2">
            <div class="prose">
              <h4>Ticket Details</h4>
            </div>
            <div class="w-full flex flex-col md:grid md:grid-cols-2 gap-4">
              <FormControl
                size="sm"
                label="Ticket ID  &ast;"
                v-model="ticketId"
                type="text"
                @focusout="
                  () => {
                    isTicketValid()
                  }
                "
              />
              <div class="hidden md:block"></div>
              <div
                v-if="ticket.data && event.data"
                class="col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4"
              >
                <FormControl
                  label="Event"
                  v-model="event.data.event_name"
                  type="text"
                  :disabled="true"
                />
                <FormControl
                  label="Ticket Tier"
                  v-model="ticket.data.tier"
                  type="text"
                  :disabled="true"
                />
              </div>
            </div>
            <ErrorMessage :message="ticketValidateError" />
          </div>
          <div class="col-span-2">
            <hr />
          </div>
          <div class="col-span-2 prose">
            <h4>Receiver Details</h4>
          </div>
          <FormControl
            v-model="receiver.receiver_email"
            label="Receiver Email &ast;"
            type="email"
            size="sm"
            placeholder="john@fossunited.org"
          />
          <FormControl
            v-model="receiver.receiver_name"
            label="Receiver Name &ast;"
            type="text"
            size="sm"
            placeholder="John Doe"
          />
          <FormControl
            v-model="receiver.designation"
            label="Designation"
            type="text"
            size="sm"
            placeholder="SDE"
          />
          <FormControl
            v-model="receiver.organization"
            label="Organization"
            type="text"
            size="sm"
            placeholder="FOSS United"
          />
          <div class="col-span-2">
            <ErrorMessage :message="ticketErrors" />
          </div>
          <div></div>
          <div class="flex items-end justify-end">
            <Button
              class="w-full md:w-2/3 font-medium"
              label="Initiate Transfer"
              variant="solid"
              theme="green"
              size="md"
              @click="initiateTranfer"
              :disabled="ticketValidateError != ''"
              :loading="createTransferDoc.loading"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import TransferSuccess from '@/components/TransferSuccess.vue'
import {
  createDocumentResource,
  FormControl,
  ErrorMessage,
  createResource,
  usePageMeta,
} from 'frappe-ui'
import { reactive, ref } from 'vue'
import { toast } from 'vue-sonner'

usePageMeta(() => {
  return {
    title: 'Ticket Transfers',
  }
})

const inSuccess = ref(false)

const transfer_settings = createDocumentResource({
  doctype: 'Ticket Transfer Settings',
  name: 'ticket_transfer_settings',
  auto: true,
})

const ticketValidateError = ref('')
const ticketErrors = ref('')

const ticketId = ref('')
const receiver = reactive({
  receiver_email: '',
  receiver_name: '',
  designation: '',
  organization: '',
})

const ticket = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Event Ticket',
      name: ticketId.value,
    }
  },
  onSuccess(data) {
    event.fetch()
  },
})

const event = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: ticket.data.event,
    }
  },
})

const isTicketValid = () => {
  if (ticketId.value === '') {
    ticketValidateError.value = 'Ticket ID is required'
    event.data = null
    ticket.data = null
    return false
  }

  createResource({
    url: 'frappe.client.get_count',
    params: {
      doctype: 'FOSS Event Ticket',
      filters: {
        name: ticketId.value,
      },
    },
    auto: true,
    onSuccess(data) {
      if (!data) {
        ticketValidateError.value = 'Invalid Ticket ID'
        return false
      }
      ticketValidateError.value = ''
      ticket.fetch()
      return true
    },
    onError(err) {
      console.log(err)
    },
  })
}

const transferErrors = () => {
  const errors = []

  if (!ticketId.value) {
    ticketValidateError.value = 'Ticket ID is required'
    errors.push('Ticket ID is required')
  }
  if (!receiver.receiver_email) {
    ticketErrors.value = 'Receiver Email is required'
    errors.push('Receiver Email is required')
  }
  if (!receiver.receiver_name) {
    ticketErrors.value = 'Receiver Name is required'
    errors.push('Receiver Name is required')
  }
  return errors
}

const createTransferDoc = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'FOSS Event Ticket Transfer',
        ticket: ticketId.value,
        receiver_email: receiver.receiver_email,
        receiver_name: receiver.receiver_name,
        designation: receiver.designation,
        organization: receiver.organization,
      },
    }
  },
  onSuccess(data) {
    inSuccess.value = true
  },
  onError(err) {
    toast.error('Failed to initiate transfer. ' + err.message)
  },
})

const initiateTranfer = () => {
  if (transferErrors().length > 0) {
    ticketErrors.value = transferErrors().join(', ')
    return
  }
  createTransferDoc.fetch()
}
</script>
