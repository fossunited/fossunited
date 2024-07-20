<template>
  <Dialog
    :model-value="showDialog"
    @update:model-value="updateShowDialog"
    :options="{
      title: 'Attendee Details',
    }"
  >
  <template #body-content>
    <div class="grid grid-cols-2 gap-4 text-base">
        <div class="col-span-2 text-base font-medium">
            <span>Status: </span><span :class="{'Pending': 'text-orange-600', 'Accepted': 'text-green-600', 'Rejected': 'text-red-600'}[participant.localhost_request_status]">{{ participant.localhost_request_status }}</span>
        </div>
        <div class="flex gap-2">
            <img :src="participant.profile_photo" alt="" class=" rounded-full h-8 w-8">
            <div class="flex flex-col gap-1">
                <div class="text-base font-medium">{{ participant.full_name }}</div>
                <div @click="redirectRoute(participant.profile_route)" class="text-sm text-green-600 hover:underline hover:cursor-pointer" v-if="participant.profile_username">{{ participant.profile_username }}</div>
            </div>
        </div>
        <div>
            <a :href="participant.git_profile" target="_blank" class="text-base hover:underline hover:cursor-pointer flex items-center gap-1">
                <span>View Git Profile</span>
                <FeatherIcon name="external-link" class="h-4 w-4 inline-block" />
            </a>
        </div>
        <div class="flex flex-col gap-1">
            <div class="text-base font-medium">Team</div>
            <div>{{ participant.team.team_name }}</div>
        </div>
        <div class="flex flex-col gap-1">
            <div class="font-medium">Project</div>
            <div v-if="participant.project_title" @click="redirectRoute(participant.project_route)" class="hover:underline hover:cursor-pointer flex items-center gap-1">{{ truncateStr(participant.project_title, 20) }}<FeatherIcon name="external-link" class="w-4 h-4 inline-block"/></div>
            <div v-else>No Project Yet</div>
        </div>
        <div class="flex flex-col gap-1">
            <div class="font-medium">Is a student?</div>
            <div>{{ participant.is_student ? 'Yes' : 'No' }}</div>
        </div>
        <div class="flex flex-col gap-1">
            <div class="font-medium">Organization/Institute</div>
            <div>{{ participant.organization }}</div>
        </div>
    </div>
  </template>
  <template #actions v-if="participant.localhost_request_status == 'Pending'">
    <div class="grid grid-cols-2 gap-4">
        <Button
            label="Reject"
            theme="red"
            size="sm"
            @click="rejectRequest(participant)"
        />
        <Button
            label="Approve"
            theme="green"
            size="sm"
            @click="acceptRequest(participant)"
        />
    </div>
  </template>
  </Dialog>
</template>
<script setup>
import { defineProps, defineEmits } from 'vue'
import { Dialog, FeatherIcon } from 'frappe-ui'
import { truncateStr } from '@/helpers/utils'
import { redirectRoute } from '@/helpers/utils';

const props = defineProps({
  participant: {
    type: Object,
    required: true,
  },
  showDialog: {
    type: Boolean,
    required: true,
    default: false,
  },
})

const emit = defineEmits(['update:showDialog', 'rejectRequest', 'acceptRequest'])

const updateShowDialog = (value) => {
  emit('update:showDialog', value)
}

const rejectRequest = (participant) => {
    emit('rejectRequest', participant)
    emit('update:showDialog', false)
}

const acceptRequest = (participant) => {
    emit('acceptRequest', participant)
    emit('update:showDialog', false)
}
</script>
