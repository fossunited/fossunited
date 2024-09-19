<template>
  <Header />
  <Dialog
    v-model="showConfirmationDialog"
    class="z-50"
    :options="{
      title: 'Confirm Project Deletion',
      message: 'Are you sure you want to delete this project?',
      actions: [
        {
          label: 'Cancel',
          theme: 'gray',
          variant: 'subtle',
          onClick: () => {
            showConfirmationDialog = false
          },
        },
        {
          label: 'Delete',
          theme: 'red',
          variant: 'solid',
          onClick: () => {
            deleteProject.fetch()
          },
        },
      ],
    }"
  />
  <div v-if="project.data" class="w-full p-4 flex items-center justify-center">
    <div class="max-w-screen-xl w-full">
      <Button
        variant="ghost"
        icon-left="arrow-left"
        label="Go Back"
        @click="
          $router.push({
            name: 'MyHackathonTeam',
          })
        "
        class="mt-4 mb-2"
      />

      <!-- Breadcrumbs -->
      <div class="flex gap-2 my-6 items-center text-base flex-wrap uppercase">
        <span class="font-semibold">My Hackathons</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
        <span class="font-semibold">{{ hackathon.data.hackathon_name }}</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
        <span>My Project</span>
      </div>

      <HackathonHeader :hackathon="hackathon" :showBanner="false" />

      <!-- Project Name & Edit -->
      <div v-if="inNameEdit" class="flex flex-col gap-2 mb-4">
        <div class="flex flex-col gap-4 md:flex-row w-full justify-between md:items-center">
          <input
            v-model="newProjectName"
            type="text"
            class="border-l-0 border-t-0 border-r-0 p-2 pt-4 font-bold text-3xl text-gray-900 active:outline-none focus:outline-none"
          />
          <div class="grid grid-cols-2 gap-2 w-full md:w-auto">
            <Button
              @click="
                () => {
                  newProjectName = project.data.title
                  inNameEdit = false
                  errorMessage = ''
                }
              "
              label="Discard"
            />
            <Button @click="handleTitleUpdate" variant="solid" theme="green" label="Update" />
          </div>
        </div>
        <ErrorMessage :message="errorMessage" />
      </div>
      <div v-else class="prose mt-4 flex items-top gap-4">
        <h2>{{ project.data.title }}</h2>
        <Button icon="edit-3" @click="inNameEdit = true" />
      </div>

      <!-- Tabs -->
      <TabsRoot :default-value="tabs[0].value" v-model="activeTab">
        <TabsList class="relative shrink-0 flex border-b border-gray-300">
          <TabsIndicator
            class="absolute px-8 left-0 h-[2px] bottom-0 w-[--radix-tabs-indicator-size] translate-x-[--radix-tabs-indicator-position] rounded-full transition-[width,transform] duration-300"
          >
            <div class="bg-gray-900 w-full h-full" />
          </TabsIndicator>
          <TabsTrigger
            v-for="tab in tabs"
            :value="tab.value"
            :key="tab.value"
            class="px-4 pb-2 mx-2 leading-none bg-white flex items-center justify-center text-base select-none rounded-tl-md outline-none cursor-pointer transition-colors duration-200"
            :class="{
              'text-gray-800 border-b border-gray-800 font-medium': activeTab === tab.value,
              'text-gray-600 hover:text-gray-800 hover:border-b hover:border-gray-400':
                activeTab !== tab.value,
            }"
            >{{ tab.label }}</TabsTrigger
          >
        </TabsList>
        <TabsContent v-for="tab in tabs" :key="tab.value" :value="tab.value" class="p-4">
          <div v-if="tab.value === 'details'">
            <HackathonProjectDetail :project="project" />
          </div>
          <div v-else-if="tab.value === 'issues'">
            <HackathonProjectIssue :project="project" @fetch-project="project.fetch()" />
          </div>
          <div v-else-if="tab.value === 'manage'">
            <HackathonProjectManage @delete-project="showConfirmationDialog = true" />
          </div>
        </TabsContent>
      </TabsRoot>
    </div>
  </div>
  <div v-if="project.loading" class="w-full h-screen flex items-center justify-center">
    <LoadingIndicator class="w-8" />
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import HackathonProjectDetail from '@/components/hackathon/HackathonProjectDetails.vue'
import HackathonProjectManage from '@/components/hackathon/HackathonProjectManage.vue'
import HackathonProjectIssue from '@/components/hackathon/HackathonProjectIssue.vue'

import { createResource, LoadingIndicator, Dialog, ErrorMessage } from 'frappe-ui'
import { inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { TabsContent, TabsIndicator, TabsList, TabsRoot, TabsTrigger } from 'radix-vue'

const route = useRoute()
const router = useRouter()
const session = inject('$session')
const showConfirmationDialog = ref(false)

const tabs = [
  {
    label: 'Details',
    value: 'details',
  },
  {
    label: 'Issues & PRs',
    value: 'issues',
  },
  {
    label: 'Manage',
    value: 'manage',
  },
]
const activeTab = ref(tabs[0].value)

const project = createResource({
  url: 'fossunited.api.hackathon.get_project_by_email',
  onSuccess(data) {
    newProjectName.value = data.title
  },
  transform(data) {
    let issue_prs = [
      {
        group: 'Issues',
        collapsed: false,
        rows: [],
      },
      {
        group: 'Pull Requests',
        collapsed: false,
        rows: [],
      },
      {
        group: 'Discussions',
        collapsed: false,
        rows: [],
      },
    ]
    data.issue_pr_table.forEach((element) => {
      if (element.type === 'Issue') {
        issue_prs[0].rows.push(element)
      } else if (element.type === 'Pull Request') {
        issue_prs[1].rows.push(element)
      } else {
        issue_prs[2].rows.push(element)
      }
    })
    issue_prs.forEach((element) => {
      if (element.rows.length === 0) {
        issue_prs = issue_prs.filter((item) => item.group !== element.group)
      }
    })
    data.issue_pr_table = issue_prs
    return data
  },
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: route.params.permalink,
  },
  auto: true,
  onSuccess(data) {
    project.update({
      params: {
        hackathon: data.name,
        email: session.user,
      },
    })
    project.fetch()
  },
})

const newProjectName = ref('')
const inNameEdit = ref(false)

const errorMessage = ref('')

const deleteProject = createResource({
  url: 'fossunited.api.hackathon.delete_project',
  makeParams() {
    return {
      hackathon: hackathon.data.name,
      team: project.data.team,
    }
  },
  onSuccess(data) {
    toast.success('Project deleted successfully')
    router.replace(`/hack/${route.params.permalink}`)
  },
  onError(error) {
    toast.error('Failed to delete project' + error.message)
  },
})

const handleTitleUpdate = () => {
  if (!newProjectName.value) {
    errorMessage.value = 'Project name cannot be empty'
    return
  } else {
    errorMessage.value = ''
  }
  updateProjectName.fetch()
}

const updateProjectName = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon Project',
      name: project.data.name,
      fieldname: 'title',
      value: newProjectName.value,
    }
  },
  onSuccess(data) {
    inNameEdit.value = false
    project.fetch()
    toast.success('Project name updated')
  },
  onError(error) {
    toast.error('Failed to update project name' + error.message)
  },
})
</script>
