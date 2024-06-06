<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-2">
      <div class="text-sm">Join a team using team code</div>
      <div class="flex items-center gap-2">
        <FormControl
          type="text"
          v-model="teamCode"
          placeholder="Enter Team Code"
          class="grow"
          description="Enter the team code shared by your team leader."
        />
        <Button variant="solid" label="Join" @click="joinThroughCode" />
      </div>
    </div>
    <div v-if="invitations.data.length > 0">
      <hr />
      <div class="text-sm flex items-center gap-1 mt-4">
        <span>Invitations</span>
        <Badge
          :label="invitations.data.length"
          theme="red"
          variant="solid"
          size="sm"
        />
      </div>
      <div class="flex flex-col py-2">
        <div
          v-for="invite in invitations.data"
          :key="invite"
          class="p-2 even:bg-gray-50 flex items-center justify-between"
        >
          <div class="flex flex-col gap-1">
            <div
              class="text-lg font-medium hover:underline hover:cursor-pointer"
              @click="openNewTab(invite.project_link.data.route)"
            >
              {{ invite.team_name }}
            </div>
            <div class="text-sm flex gap-1 items-end">Invited by <span @click="openNewTab(invite.sender_profile.data.route)" class="hover:underline hover:cursor-pointer">{{ invite.sender_name }}</span></div>
          </div>
          <div class="flex gap-1">
            <Button icon="check" theme="green" @click="acceptInvite(invite.name)"/>
            <Button icon="x" theme="red" @click="rejectInvite(invite.name)"/>
          </div>
        </div>
      </div>
    </div>
</div>
</template>
<script setup>
import { FormControl, createResource, Badge, createDocumentResource } from 'frappe-ui'
import Button from 'frappe-ui/src/components/Button.vue'
import { ref, defineProps, onMounted } from 'vue'

const teamCode = ref('')

const props = defineProps({
  hackathon: {
    type: Object,
    required: true,
  },
  invitations: {
    type: Object,
    default: {},
  },
})

onMounted(() => {
  if (props.invitations.data.length) {
    Object.entries(props.invitations.data).forEach(([key, value]) => {
      value.sender_profile = createResource({
        url: 'fossunited.fossunited.utils.get_foss_profile',
        params: {
          email: value.requested_by,
        },
        fields: ['route', 'full_name', 'profile_photo'],
        auto: true,
        realtime: true,
      })
      value.project_link = createResource({
        url: 'frappe.client.get_value',
        params: {
          doctype: 'FOSS Hackathon Project',
          fieldname: 'route',
          filters: {
            team: value.team,
            hackathon: value.hackathon,
          },
        },
        auto: true,
        realtime: true,
      })

      return value
    })
  }
})

const openNewTab = (route) => {
  window.open(document.location.origin + '/' + route, '_blank')
}

const joinThroughCode = () => {}

const acceptInvite = (inviteId) => {
    console.log(inviteId, 'accept')
    createResource({
        url: 'frappe.client.set_value',
        params: {
            doctype: 'FOSS Hackathon Join Team Request',
            name: inviteId,
            fieldname: 'status',
            value: 'Accepted',
        },
        auto: true,
        onSuccess: (data) => {
            window.location.reload()
        },
        onError(error) {
            console.error(error)
        },
    })
}

const rejectInvite = (inviteId) => {
    console.log(inviteId, 'reject')
    createResource({
        url: 'frappe.client.set_value',
        params: {
            doctype: 'FOSS Hackathon Join Team Request',
            name: inviteId,
            fieldname: 'status',
            value: 'Rejected',
        },
        auto: true,
        onSuccess: (data) => {
            props.invitations.fetch()
        },
        onError(error) {
            console.error(error)
        },
    })
}
</script>
