<template>
  <div class="flex gap-4 mt-0 w-full border-b px-2">
    <div
      v-for="section in sections"
      class="p-1 cursor-pointer transition-colors text-base"
      :class="
        inInvite == section.value
          ? 'text-gray-900 border-b-2 border-gray-900 font-medium'
          : ' text-gray-600'
      "
      @click="inInvite = section.value"
    >
      {{ section.name }}
    </div>
  </div>
  <div class="px-2 py-3">
    <div v-if="inInvite" class="mt-2">
      <div class="text-sm">Invite members to join your team</div>
      <div class="flex gap-2 my-2">
        <FormControl
          class="grow"
          type="email"
          v-model="inviteEmail"
          placeholder="john.doe@fossunited.org"
        />
        <Button label="Invite" @click="createJoinRequest" variant="solid" />
      </div>
      <div class="w-full text-sm font-medium uppercase my-3 text-center">
        Or
      </div>
      <div class="flex gap-2 items-center text-base flex-wrap">
        <div class="">Invite via team code:</div>
        <CopyToClipboard :route="teamCode" />
      </div>
      <div class="mt-2" v-if="outgoingInvites.data.length > 0">
        <hr class="my-4" />
        <div class="text-sm mb-2">Sent Invites:</div>
        <div
          v-for="invite in outgoingInvites.data"
          class="flex items-center flex-wrap w-full gap-2 justify-between p-2 rounded-sm even:bg-gray-50"
        >
          <div class="text-sm text-gray-600">
            {{ invite.reciever_email }}
          </div>
          <Badge
            :label="invite.status"
            :theme="
              { Pending: 'orange', Accepted: 'green', Rejected: 'red' }[
                invite.status
              ]
            "
          />
        </div>
      </div>
    </div>
    <div v-else>
      <div class="pt-2 px-2 flex flex-col gap-4">
        <div
          v-for="member in props.team.data.members"
          class="flex items-center w-full justify-between gap-2"
        >
            <div class="flex gap-2 items-center">
                <img :src="member.profile_photo" class="w-8 h-8 rounded-full" />
                <div>
                  <div class="text-base font-medium">{{ member.full_name }}</div>
                  <div class="text-sm text-gray-600">{{ member.email }}</div>
                </div>
            </div>
            <Button
                v-if="member.email != props.team.data.owner"
                :label="member.email == session.user ? 'Leave' : 'Remove'"
                theme="red"
                @click="removeTeamMember(member)"
            />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps, onMounted, ref, inject } from 'vue'
import {
  createListResource,
  FormControl,
  Badge,
  createResource,
} from 'frappe-ui'
import { toast } from 'vue-sonner'
import CopyToClipboard from '@/components/CopyToClipboardComponent.vue'

const inInvite = ref(0)
const inviteEmail = ref('')
const teamCode = ref('')
const session = inject('$session')

const sections = ref([
  {
    name: 'Members',
    value: 0,
  },
  {
    name: 'Invite',
    value: 1,
  },
])

const props = defineProps({
  team: {
    type: Object,
    required: true,
  },
})

const outgoingInvites = createListResource({
  doctype: 'FOSS Hackathon Join Team Request',
  fields: ['*'],
  pageLength: 999,
})

onMounted(() => {
  teamCode.value = props.team.data.name
  outgoingInvites.update({
    filters: {
      team: props.team.data.name,
      hackathon: props.team.data.hackathon,
      is_outgoing_request: 1,
    },
  })
  outgoingInvites.fetch()
})

const createJoinRequest = () => {
  const invite = createResource({
    url: 'frappe.client.insert',
    makeParams() {
      return {
        doc: {
          doctype: 'FOSS Hackathon Join Team Request',
          team: props.team.data.name,
          hackathon: props.team.data.hackathon,
          requested_by: session.user,
          reciever_email: inviteEmail.value,
          is_outgoing_request: 1,
        },
      }
    },
    onSuccess(data) {
      outgoingInvites.fetch()
      inviteEmail.value = ''
      toast.success('Invite sent successfully')
    },
    onError(error) {
      toast.error('Failed to send invite' + error)
    },
  })
  invite.fetch()
}

const removeTeamMember = (member) => {
  const newMembers = props.team.data.members.filter(
    (m) => m.email != member.email
  )
  const team = createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Hackathon Team',
        name: props.team.data.name,
        fieldname: 'members',
        value: newMembers,
      }
    },
    onSuccess() {
      props.team.fetch()
      toast.success('Member removed successfully')
    },
    onError(error) {
      toast.error('Failed to remove member' + error)
    },
  })
  team.fetch()
}
</script>
