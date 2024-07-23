<template>
  <Header />
  <Dialog
    v-model="showConfirmationDialog"
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
          }
        },
        {
          label: 'Delete',
          theme: 'red',
          variant: 'solid',
          onClick: () => {
            deleteProject.fetch()
          }
        }
      ]
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
      <div class="flex gap-2 my-6 items-center text-base uppercase">
        <span class="font-semibold">My Hackathons</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="m8.25 4.5 7.5 7.5-7.5 7.5"
          />
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
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="m8.25 4.5 7.5 7.5-7.5 7.5"
          />
        </svg>
        <span>My Project</span>
      </div>
      <HackathonHeader :hackathon="hackathon" :showBanner="false" />
      <div
        v-if="inNameEdit"
        class="flex flex-col gap-4 md:flex-row w-full justify-between md:items-center mb-4"
      >
        <input
          v-model="newProjectName"
          type="text"
          class="border-l-0 border-t-0 border-r-0 p-2 pt-4 font-bold text-3xl text-gray-900 active:outline-none focus:outline-none"
        />
        <div class="grid grid-cols-2 gap-2 w-full md:w-auto">
          <Button
            @click="
              () => {
                inNameEdit = false
                errorMessage.value = ''
              }
            "
            label="Discard"
          />
          <Button
            @click="handleTitleUpdate"
            variant="solid"
            theme="green"
            label="Update"
          />
        </div>
      </div>
      <div v-else class="prose mt-4 flex items-top gap-4">
        <h2>{{ project.data.title }}</h2>
        <Button icon="edit-3" @click="inNameEdit = true" />
      </div>
      <hr />
      <div class="flex flex-col md:grid md:grid-cols-2 my-4 gap-4 md:items-center">
        <div class="hidden md:block"></div>
        <div class="flex flex-col gap-2">
          <div class="text-sm uppercase text-gray-600 font-medium">Delete Project</div>
          <p class="text-sm">Delete this project and create something new.</p>
          <Button
            icon-left="trash"
            label="Trash"
            theme="red"
            class="w-fit"
            @click="showConfirmationDialog=true"
          />
        </div>
        <div class="flex flex-col py-1">
          <div class="text-xs text-gray-600">Project's Public Page</div>
          <CopyToClipboard :route="getRoute(project.data.route)" />
        </div>
        <FormControl
          label="Short Description"
          v-model="project.data.short_description"
          placeholder="Enter a short description of the project"
        />
        <FormControl
          label="Repository Link"
          v-model="project.data.repo_link"
          :disabled="project.data.is_partner_project"
        >
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
              class="icon w-5 icon-tabler icons-tabler-outline icon-tabler-brand-github"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path
                d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"
              />
            </svg>
          </template>
        </FormControl>
        <FormControl label="Demo Link" v-model="project.data.demo_link" />
        <TextEditor
          class="col-span-2 mt-2"
          label="Project Description"
          :modelValue="project.data.description"
          placeholder="Enter a detailed description of the project"
          @update:modelValue="($event) => (project.data.description = $event)"
        />
      </div>
      <div>
        <ErrorMessage :message="errorMessage" />
        <div class="grid grid-cols-1 md:grid-cols-2 place-items-end">
          <div></div>
          <Button
            @click="handleProjectUpdate"
            variant="solid"
            theme="green"
            label="Save"
            size="md"
            class="w-full md:w-2/3"
          />
        </div>
      </div>
    </div>
  </div>
  <div
    v-if="project.loading"
    class="w-full h-screen flex items-center justify-center"
  >
    <LoadingIndicator class="w-8" />
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import CopyToClipboard from '@/components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/TextEditor.vue'
import {
  createResource,
  LoadingIndicator,
  FormControl,
  ErrorMessage,
  Dialog,
} from 'frappe-ui'
import { inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const session = inject('$session')
const showConfirmationDialog = ref(false)

const project = createResource({
  url: 'fossunited.api.hackathon.get_project_by_email',
  onSuccess(data) {
    newProjectName.value = data.title
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
const getRoute = (route) => {
  return `${window.location.origin}/${route}`
}

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
  }
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

const updateProjectErrors = () => {
  const errors = []

  if (!project.data.title) {
    errors.push('Project name cannot be empty')
  }
  if (!project.data.short_description) {
    errors.push('Short description cannot be empty')
  }
  if (!project.data.description) {
    errors.push('Description cannot be empty')
  }
  if (!project.data.repo_link) {
    errors.push('Repository link cannot be empty')
  }
  if (
    project.data.repo_link &&
    !project.data.repo_link.startsWith('https://')
  ) {
    errors.push('Enter a valid repo link')
  }

  return errors
}

const handleProjectUpdate = () => {
  if (updateProjectErrors().length) {
    errorMessage.value = updateProjectErrors().join(', ')
    return
  } else {
    errorMessage.value = ''
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Hackathon Project',
        name: project.data.name,
        fieldname: {
          title: project.data.title,
          short_description: project.data.short_description,
          description: project.data.description,
          repo_link: project.data.repo_link,
          demo_link: project.data.demo_link,
        },
      }
    },
    auto: true,
    onSuccess(data) {
      toast.success('Project updated successfully')
    },
    onError(error) {
      toast.error('Failed to update project' + error.message)
    },
  })
}
</script>
