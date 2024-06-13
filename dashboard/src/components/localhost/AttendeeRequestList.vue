<template>
  <div class="prose">
    <h4>Requests</h4>
  </div>
  <div class="flex gap-3 flex-wrap">
    <Button
      v-for="filter in filters"
      :label="filter.label"
      size="sm"
      :variant="filter.isActive ? 'solid' : 'outline'"
      @click="handleFilter(filter)"
    />
  </div>
  <div class="w-full place-items-center">
    <div class="my-2" v-if="requestByGroup.data">
      <div
        v-for="(members, team) in requestByGroup.data"
        class="my-2 p-4 flex flex-col"
        :class="members.length > 1 ? ' rounded border-2 ' : ''"
      >
        <div class="mb-1 flex items-center justify-between">
          <span class="text-base font-medium" v-if="members[0].team">
            {{ members[0].team.team_name }}
          </span>
          <span v-else class="text-base font-medium"> No Team Assigned </span>
        </div>
        <div class="divide-y-2">
          <div
            v-for="member in members"
            class="p-2 flex justify-between w-full"
            :class="members.length > 1 ? 'bg-white py-3' : ''"
          >
            <div class="text-base flex flex-col justify-center gap-2">
              <div
                class="hover:underline flex gap-2 hover:cursor-pointer"
                @click="redirectToProfile(member.profile_route)"
              >
                {{ member.full_name }}
              </div>
              <div class="flex items-center gap-2 flex-wrap">
                <Badge
                  :label="member.localhost_request_status"
                  size="sm"
                  :theme="
                    { Pending: 'orange', Accepted: 'green', Rejected: 'red' }[
                      member.localhost_request_status
                    ]
                  "
                />
                <Badge v-if="member.is_student" label="Student">
                  <template #prefix>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon w-4 h-4 icon-tabler icons-tabler-outline icon-tabler-school"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M22 9l-10 -4l-10 4l10 4l10 -4v6" />
                      <path d="M6 10.6v5.4a6 3 0 0 0 12 0v-5.4" />
                    </svg>
                  </template>
                </Badge>
                <div>
                  <a
                    :href="member.git_profile"
                    class="text-sm hover:underline hover:cursor-pointer flex items-center"
                    target="_blank"
                  >
                    <span>Git Profile</span>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon w-4 h-4 icon-tabler icons-tabler-outline icon-tabler-arrow-up-right"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M17 7l-10 10" />
                      <path d="M8 7l9 0l0 9" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
            <div
              class="flex gap-2 text-sm"
              v-if="member.localhost_request_status == 'Pending'"
            >
              <Button
                theme="green"
                icon="check"
                @click="acceptRequest(member)"
              />
              <Button
                theme="red"
                icon="x"
                @click="rejectRequest(member)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-sm font-medium text-gray-700 w-full my-5 uppercase">
      <p>No Requests</p>
    </div>
    <div class="w-full p-4 flex justify-center" v-if="requestByGroup.loading">
      <LoadingIndicator class="w-5" />
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { LoadingIndicator, createResource, Badge, Button } from 'frappe-ui'
import { ref } from 'vue'

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})

const filters = ref([
  {
    label: 'Show Pending Requests',
    isActive: false,
    value: 'Pending',
  },
  {
    label: 'Show Accepted Requests',
    isActive: false,
    value: 'Accepted',
  },
])

const requestByGroup = createResource({
  url: 'fossunited.api.hackathon.get_localhost_requests_by_team',
  params: {
    hackathon: props.localhost.doc.parent_hackathon,
    localhost: props.localhost.doc.name,
  },
  auto: true,
})

const redirectToProfile = (route) => {
  window.open(document.location.origin + '/' + route, '_blank')
}

const changeLocalhostRequestStatus = (id, status) => {
  return createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: id,
      fieldname: 'localhost_request_status',
      value: status,
    },
    onSuccess(data) {
      requestByGroup.fetch()
    },
  })
}

const acceptRequest = (member) => {
  changeLocalhostRequestStatus(member.name, 'Accepted').fetch()
}

const rejectRequest = (member) => {
  changeLocalhostRequestStatus(member.name, 'Rejected').fetch()
}

const handleFilter = (filter) => {
    filter.isActive = !filter.isActive
    if (filter.isActive){
        toggleOtherFilters(filter)
        requestByGroup.update({
            params: {
                hackathon: props.localhost.doc.parent_hackathon,
                localhost: props.localhost.doc.name,
                status: [filter.value]
            }
        })
        requestByGroup.fetch()
    }
    else{
        requestByGroup.update({
            params: {
                hackathon: props.localhost.doc.parent_hackathon,
                localhost: props.localhost.doc.name,
            }
        })
        requestByGroup.fetch()
    }
}

const toggleOtherFilters = (filter) => {
    filters.value.forEach(f => {
        if (f.value !== filter.value){
            f.isActive = false
        }
    })
}

</script>
