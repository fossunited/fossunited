<template>
  <Dialog class="z-50" v-model="inTeamManage">
    <template #body-title>
      <h3 class="text-xl font-semibold">Manage Team</h3>
    </template>
    <template #body-content>
      <HackathonTeamMember :team="team" />
    </template>
  </Dialog>
  <Header />
  <div
    v-if="hackathon.data"
    class="w-full p-4 flex items-center justify-center"
  >
    <div v-if="team.data" class="max-w-screen-xl w-full">
      <HackathonHeader :hackathon="hackathon" :showBanner="false" />
      <div
        v-if="inNameEdit"
        class="flex flex-col gap-4 md:flex-row w-full justify-between md:items-center mb-4"
      >
        <input
          v-model="newTeamName"
          type="text"
          class="border-l-0 border-t-0 border-r-0 p-2 pt-4 font-bold text-3xl text-gray-900 active:outline-none focus:outline-none"
        />
        <div class="grid grid-cols-2 gap-2 w-full md:w-auto">
          <Button @click="inNameEdit = false" label="Discard" />
          <Button
            @click="updateTeamName"
            variant="solid"
            theme="green"
            label="Update"
          />
        </div>
      </div>
      <div v-else class="prose mt-4 flex items-top gap-4">
        <h2>{{ team.data.team_name }}</h2>
        <Button icon="edit-3" @click="inNameEdit = true" />
      </div>
      <hr />
      <div class="py-4 my-4 gap-6 grid grid-cols-1 md:grid-cols-2">
        <div
          v-if="hasProject.data == 0"
          class="rounded border-2 text-gray-700 border-gray-700 bg-gray-50 border-dashed flex flex-col justify-between p-5 gap-8"
        >
          <div class="text-base font-semibold uppercase">Project</div>
          <div class="flex justify-between items-end">
            <div class="flex flex-col gap-2">
              <div class="font-medium text-lg uppercase">No Project Found</div>
              <div class="text-sm">Set up your project for the hackathon</div>
            </div>
            <Button
              variant="solid"
              class="w-fit"
              size="sm"
              @click="
                $router.push(
                  `/hack/${hackathon.data.permalink}/create-project?team=${team.data.name}`,
                )
              "
              label="Create"
            />
          </div>
        </div>
        <div
          v-else
          class="rounded bg-gray-50 border border-gray-400 flex flex-col justify-between p-5 gap-8"
        >
          <div class="text-base font-semibold uppercase">Project</div>
          <div class="flex justify-between items-end">
            <div class="flex flex-col gap-2">
              <div class="font-medium text-lg uppercase break-all">
                {{ project.data?.title }}
              </div>
              <div class="text-sm">{{ project.data?.short_description }}</div>
            </div>
            <Button
              variant="solid"
              class="w-fit"
              size="sm"
              label="Manage"
              @click="
                $router.push({
                  name: 'MyHackathonProject',
                })
              "
            />
          </div>
        </div>
        <div class="rounded border flex flex-col justify-between p-5 gap-8">
          <div class="text-base font-semibold uppercase">Team</div>
          <div class="flex justify-between items-end">
            <div class="font-medium text-lg uppercase">
              {{ team.data.members.length }} Members
            </div>
            <Button
              class="w-fit"
              size="sm"
              @click="inTeamManage = true"
              label="Manage"
            />
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-2">
        <div
          class="w-full bg-gray-50 text-gray-800 rounded p-4"
          v-if="hackathon.data.hackathon_rules"
        >
          <h3 class="text-md font-semibold">Hackathon Rules</h3>
          <div
            class="prose leading-normal"
            v-html="hackathon.data.hackathon_rules"
          ></div>
        </div>
        <div
          class="w-full bg-gray-50 text-gray-800 rounded p-4"
          v-if="hackathon.data.hackathon_faq"
        >
          <h3 class="text-md font-semibold">Hackathon FAQs</h3>
          <div
            class="prose leading-normal"
            v-html="hackathon.data.hackathon_faq"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import HackathonTeamMember from '@/components/hackathon/HackathonTeamMember.vue'
import { createResource, usePageMeta, Dialog } from 'frappe-ui'
import { inject, ref } from 'vue'
import { useRoute } from 'vue-router'

const session = inject('$session')
const route = useRoute()
const newTeamName = ref('')
const inNameEdit = ref(false)
const inTeamManage = ref(false)
const inAddMember = ref(false)

usePageMeta(() => ({
  title: 'My Team',
}))

const project = createResource({
  url: 'fossunited.api.hackathon.get_project_by_team',
})

const hasProject = createResource({
  url: 'frappe.client.get_count',
  onSuccess(data) {
    if (data > 0) {
      project.update({
        params: {
          hackathon: hackathon.data.name,
          team: team.data.name,
        },
      })
      project.fetch()
    }
  },
})

const team = createResource({
  url: 'fossunited.api.hackathon.get_team_by_member_email',
  onSuccess(data) {
    newTeamName.value = data.team_name
    hasProject.update({
      params: {
        doctype: 'FOSS Hackathon Project',
        filters: {
          team: data.name,
          hackathon: hackathon.data.name,
        },
      },
    })
    hasProject.fetch()
  },
  transform(data) {
    data.members.forEach((member) => {
      let profile = createResource({
        url: 'fossunited.fossunited.utils.get_foss_profile',
        params: {
          email: member.email,
        },
        auto: true,
        onSuccess(data) {
          member.profile_photo = data.profile_photo
            ? data.profile_photo
            : '/assets/fossunited/images/defaults/user_profile_image.png'
        },
      })
    })
    return data
  },
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: route.params.permalink,
  },
  auto: true,
  onSuccess: (data) => {
    team.update({
      params: {
        hackathon: data.name,
        email: session.user,
      },
    })
    team.fetch()
  },
})

const updateTeamName = () => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Team',
      name: team.data.name,
      fieldname: 'team_name',
      value: newTeamName.value,
    },
    auto: true,
    onSuccess: () => {
      inNameEdit.value = false
      team.fetch()
    },
    onError: (error) => {
      console.log(error)
    },
  })
}

const removeMember = (member) => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Team',
      name: team.data.name,
      fieldname: 'members',
      value: team.data.members.filter((m) => m.email != member.email),
    },
    auto: true,
    onSuccess: () => {
      team.fetch()
    },
    onError: (error) => {
      console.log(error)
    },
  })
}
</script>
