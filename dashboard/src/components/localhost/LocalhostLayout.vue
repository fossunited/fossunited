<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
  />

  <div v-if="isValidated" class="w-full min-h-screen flex overflow-x-hidden">
    <SideNavbar title="Manage Localhost" :menu-items="sidebarMenuItems" />

    <div class="flex-1 p-4 md:ml-[220px] min-w-0">
      <div class="max-w-screen-xl mx-auto min-w-0">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { Dialog, createResource } from 'frappe-ui'
import SideNavbar from '@/components/NewAppSidebar.vue'
import { LocalhostValidation } from '@/components/localhost/LocalhostValidation'

const route = useRoute()
const router = useRouter()

const { isValidated, dialogMessage, showDialog, validateSessionUser } = LocalhostValidation(
  route.params.id,
  'MyLocalhosts',
)

const sidebarMenuItems = computed(() => [
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Back',
        route: '/localhost',
      },
    ],
  },
  {
    items: [
      {
        label: 'Edit Localhost',
        route: `/localhost/${route.params.id}/edit`,
      },
      {
        label: 'Manage Attendees',
        route: `/localhost/${route.params.id}`,
      },
      {
        label: 'Localhost Mailing',
        route: `/localhost/${route.params.id}/mailing`,
      },
    ],
  },
])

onMounted(() => {
  validateSessionUser()
})
</script>
