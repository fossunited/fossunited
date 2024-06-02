<template>
  <Header />
  <div
    v-if="hackathon.data"
    class="flex w-full p-4 items-center justify-center"
  >
    <div class="w-full max-w-screen-xl">
      <HackathonHeader :hackathon="hackathon" :showBanner="false" />
      <hr class="my-6" />
      <div
        v-if="inSelectProjectType"
        class="grid grid-cols-1 gap-5 md:grid-cols-2 pt-6 md:p-0"
      >
        <div
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center"
          :class="
            hackathon.data.enable_oss_contributon_projects
              ? 'md:border-r-2 sm:col-span-1'
              : 'md:col-span-2'
          "
        >
          <div
            class="px-4 py-2 w-3/4 text-center uppercase border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
            @click="
              () => {
                inSelectProjectType = false
                inCreateProject = true
              }
            "
          >
            Create Project
          </div>
          <p class="text-base text-center leading-normal">
            Create and work on your own project.
          </p>
        </div>
        <div
          v-if="hackathon.data.enable_oss_contributon_projects"
          class="md:hidden w-full text-center font-medium"
        >
          OR
        </div>
        <div
          v-if="hackathon.data.enable_oss_contributon_projects"
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center"
        >
          <div
            class="px-4 py-2 uppercase w-3/4 text-center border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
          >
            Contribute
          </div>
          <p class="text-base text-center leading-normal">
            Contribute to other open-source projects.
          </p>
        </div>
      </div>
      <div v-if="inCreateProject">
        <Button
          variant="ghost"
          label="Go Back"
          icon-left="arrow-left"
          @click="
            () => {
              inCreateProject = false
              inSelectProjectType = true
            }
          "
        />
        <div class="prose mt-5 mb-3">
          <h3>Create Project</h3>
        </div>
        <div class="grid my-4 gap-4 grid-cols-1 md:grid-cols-2">
          <FormControl label="Title" v-model="project.title" />
          <FormControl
            label="Short Description"
            v-model="project.short_description"
            description="One line description for your project."
          />
          <FormControl label="Repository Link" v-model="project.repo_link">
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
          <FormControl
            label="Demo Link"
            v-model="project.demo_link"
            description="Demo link for the project. Can be a URL to a video demo, hosted app/website link etc. This can be added later."
          />
          <div class="flex flex-col gap-2 col-span-2">
            <div class="text-xs text-gray-600">Project Description</div>
            <TextEditor
              :placeholder="'Write a detailed description of your project'"
              :modelValue="project.description"
              @update:modelValue="($event) => (project.description = $event)"
            />
          </div>
        </div>
        <ErrorMessage :message="errorMessage"/>
        <div class="grid grid-cols-1 md:grid-cols-2 place-items-end">
          <div></div>
          <Button
            @click="handleCreateProject"
            label="Create Project"
            theme="green"
            variant="solid"
            class="md:w-2/3"
            size="md"
            :loading="createProject.loading"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import TextEditor from '@/components/TextEditor.vue'
import { createResource, FormControl, ErrorMessage } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { inject, onMounted, reactive, ref } from 'vue'
import { toast } from 'vue-sonner'

const session = inject('$session')
const route = useRoute()
const router = useRouter()

const inSelectProjectType = ref(true)
const inCreateProject = ref(false)
const inContribute = ref(false)

const project = reactive({
    hackathon: '',
    team: '',
    title: '',
    repo_link: '',
    demo_link: '',
    short_description: '',
    description: '',
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: route.params.permalink,
  },
  auto: true,
  onSuccess(data) {
    project.hackathon = data.name
  },
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  project.team = params.get('team')
})

const errorMessage = ref('')

const validateCreateProject = () => {
  let errors = []

  if (!project.title) {
    errors.push('Title is required')
  }
  if (!project.short_description) {
    errors.push('Write a short description')
  }
  if (!project.description) {
    errors.push('Project description is required')
  }
  if (!project.repo_link) {
    errors.push('Repository link is required')
  }
  if(project.repo_link && !project.repo_link.startsWith('https://')){
    errors.push("Enter a valid repo link")
  }
  return errors
}

const createProject =   createResource({
    url: 'fossunited.api.hackathon.create_project',
    makeParams(){
      return {
        hackathon: project.hackathon,
        team: project.team,
        project: project,
      }
    },
    onSuccess(data) {
        // TODO: Redirect to project Manage Page
        createResource({
          url: 'frappe.client.set_value',
          makeParams() {
            return {
              doctype: 'FOSS Hackathon Team',
              name: route.query.team,
              fieldname: 'project',
              value: data.name,
            }
          },
          auto: true,
        })
        router.push({
            name: 'MyHackathonProject'
        })
    },
    onError(error) {
        console.log(error)
        toast.error('Failed to create project')
    },
  })

const handleCreateProject = () => {
  const errors = validateCreateProject()
  if (errors.length) {
    errorMessage.value = errors.join(', ')
    return
  }
  else{
    errorMessage.value = ''
  }
  createProject.fetch()
}
</script>
