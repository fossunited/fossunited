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
    <div v-if="transferStatus" class="max-w-screen-xl w-full flex flex-col items-start">
      <div class="flex flex-col justify-between md:flex-row md:items-center w-full p-2">
        <div>
          <HackathonHeader
            v-if="hackathon_doc.data"
            :hackathon="hackathon_doc"
            :show-banner="false"
          />
        </div>
        <div class="flex flex-col md:items-end">
          <LocalhostHeader v-if="localhost_doc.data" :localhost="localhost_doc.data" />
        </div>
      </div>
      <StatusMessage :status="transferStatus" />
    </div>
    <div v-else class="flex w-full justify-center items-center">
      <LoadingIndicator class="w-6" />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import StatusMessage from '@/components/localhost/StatusMessage.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'
import {
  createDocumentResource,
  createResource,
  Dialog,
  usePageMeta,
  LoadingIndicator,
} from 'frappe-ui'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const participant = route.query.participant
const localhost = route.query.localhost
const status = route.query.status

const showDialog = ref(false)
const dialogMessage = ref('')

const transferStatus = ref('')

usePageMeta(() => {
  return {
    title: 'Localhost Attendance Process',
  }
})

onMounted(() => {
  if (!isValidStatus()) {
    return
  }
  validateLocalhost.fetch()
  validateParticipant.fetch()
})

const participant_doc = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon Participant',
      name: participant,
      fields: ['name'],
    }
  },
  onSuccess(data) {
    if (status == 1) {
      confirmAttendance()
    } else {
      rejectAttendance()
    }
  },
  onError(err) {
    showDialog.value = true
    dialogMessage.value = err.message
  },
})

const hackathon_doc = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon',
      name: localhost_doc.data.parent_hackathon,
    }
  },
  onSuccess(data) {},
})

const localhost_doc = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon LocalHost',
      filters: {
        name: localhost,
      },
      fieldname: ['localhost_name', 'parent_hackathon', 'city', 'state', 'location', 'map_link'],
    }
  },
  onSuccess(data) {
    hackathon_doc.fetch()
  },
})

const isValidStatus = () => {
  if (status != 0 && status != 1) {
    showDialog.value = true
    dialogMessage.value = 'Invalid status'
    return false
  }
  return true
}

const validateLocalhost = createResource({
  url: 'fossunited.api.hackathon.is_valid_localhost',
  makeParams() {
    return {
      localhost_id: localhost,
    }
  },
  onSuccess(data) {
    if (!data) {
      showDialog.value = true
      dialogMessage.value = 'Invalid Localhost'
    } else {
      localhost_doc.fetch()
    }
  },
})

const validateParticipant = createResource({
  url: 'fossunited.api.hackathon.validate_participant_for_localhost',
  makeParams() {
    return {
      participant_id: participant,
    }
  },
  onSuccess(data) {
    if (data) {
      participant_doc.fetch()
    }
  },
  onError(err) {
    showDialog.value = true
    dialogMessage.value = err.messages.join('\n')
  },
})

const changeLocalhostStatus = (_status) => {
  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Hackathon Participant',
        name: participant,
        fieldname: 'localhost_request_status',
        value: _status,
      }
    },
    onSuccess(data) {
      transferStatus.value = _status
    },
    onError(err) {
      showDialog.value = true
      dialogMessage.value = err.message
    },
    auto: true,
  })
}

const confirmAttendance = () => {
  changeLocalhostStatus('Accepted')
}

const rejectAttendance = () => {
  changeLocalhostStatus('Rejected')
}
</script>
