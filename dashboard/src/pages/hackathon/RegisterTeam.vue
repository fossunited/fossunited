<template>
  <Header />
  <Dialog
    v-model="show_dialog"
    :options="{
      title: dialog_content.title,
      message: dialog_content.message,
    }"
  />
  <div class="w-full min-h-screen flex justify-center">
    <div class="container p-8" v-if="hackathon.data">
      <div class="flex gap-2 mb-10 items-center">
        <a
          :href="redirectToHackathon"
          class="font-semibold text-base hover:underline"
          >{{ hackathon.data.hackathon_name }}</a
        >
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
        <span class="text-base">Register</span>
      </div>
      <img
        v-if="hackathon.data.hackathon_logo"
        :src="hackathon.data.hackathon_logo"
        class="h-12 mb-4"
      />
      <h1 class="text-3xl font-medium">
        Register For
        <span class="font-bold">{{ hackathon.data.hackathon_name }}</span>
      </h1>
      <div v-html="hackathon.data.registration_description" class="mt-2"></div>
      <hr class="my-4" />
      <div class="w-full">
        <h3 class="text-lg font-semibold">Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-y-4 my-3">
          <FormControl type="text" label="Team Name" v-model="team.team_name" />
          <div></div>
          <div
            class="col-span-2 bg-gray-50 p-4 rounded-sm outline-dashed outline-2 outline-gray-600 mt-2"
          >
            <h5 class="text-base text-gray-800 font-medium">Team Members</h5>
            <p class="text-sm mt-2 text-gray-600">
              You can add members after registration.
            </p>
          </div>
        </div>
        <div v-if="localhost.data" class="mt-6">
          <h5 class="text-base font-medium text-gray-800">
            Where will you hack from?
          </h5>
          <RadioGroup
            v-model="selected_attendance"
            class="grid sm:grid-cols-3 lg:grid-cols-5 gap-2 my-3"
          >
            <RadioGroupOption
              as="template"
              v-for="option in attend_option"
              :key="option.value"
              :value="option"
              v-slot="{ active, checked }"
            >
              <div
                :class="[checked ? 'bg-gray-50 border-gray-700' : 'bg-white ']"
                class="relative flex cursor-pointer rounded-sm px-5 py-3 border focus:outline-none hover:border-gray-500 transition-[border]"
              >
                <div class="flex w-full items-center justify-center">
                  <div class="flex flex-col gap-2 items-center">
                    <svg
                      v-if="option.title == 'Remote'"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon icon-tabler icons-tabler-outline icon-tabler-world stroke-gray-900"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
                      <path d="M3.6 9h16.8" />
                      <path d="M3.6 15h16.8" />
                      <path d="M11.5 3a17 17 0 0 0 0 18" />
                      <path d="M12.5 3a17 17 0 0 1 0 18" />
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon icon-tabler icons-tabler-outline icon-tabler-map-pin-code"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
                      <path
                        d="M11.85 21.48a1.992 1.992 0 0 1 -1.263 -.58l-4.244 -4.243a8 8 0 1 1 13.385 -3.585"
                      />
                      <path d="M20 21l2 -2l-2 -2" />
                      <path d="M17 17l-2 2l2 2" />
                    </svg>
                    <div class="text-sm">
                      <RadioGroupLabel as="p" class="font-medium">
                        {{ option.title }}
                      </RadioGroupLabel>
                    </div>
                  </div>
                </div>
              </div>
            </RadioGroupOption>
          </RadioGroup>
          <div
            v-if="selected_attendance.value == 1"
            class="grid grid-cols-1 md:grid-cols-2"
          >
            <FormControl
              type="select"
              label="Select LocalHost"
              v-model="team.localhost"
              :placeholder="localhost.data[0].localhost_name"
              :options="
                localhost.data.map((item) => ({
                  label: item.localhost_name,
                  value: item.name,
                }))
              "
            />
          </div>
          <div
            class="flex flex-col items-center sm:flex-row gap-3 bg-yellow-50 w-full p-4 text-sm rounded-sm my-4 text-yellow-600 outline-2 outline-dashed"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#000000"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-7 shrink-0 stroke-yellow-600 icon icon-tabler icons-tabler-outline icon-tabler-alert-circle"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
            <p class="leading-normal text-center sm:text-left">
              Please note that attendance at offline venues is limited by seat
              availability. Our team will review your application to attend the
              hackathon.<br />
              If there are not enough seats available, your application to
              attend in person may be <b>declined</b>, and you may need to
              participate remotely.
            </p>
          </div>
        </div>
        <hr class="my-7" />

        <!-- PROJECT DETAILS -->
        <h3 class="text-lg font-semibold mb-4">Project Details</h3>
        <div v-if="hackathon.data.has_partner_projects">
          <h5 class="text-base font-medium text-gray-800">Type of Project</h5>
          <RadioGroup
            v-model="selected_project_option"
            class="grid sm:grid-cols-3 lg:grid-cols-5 gap-2 my-3"
          >
            <RadioGroupOption
              as="template"
              v-for="option in project_options"
              :key="option.value"
              :value="option"
              v-slot="{ active, checked }"
            >
              <div
                :class="[checked ? 'bg-gray-50 border-gray-700' : 'bg-white ']"
                class="relative flex cursor-pointer rounded-sm px-5 py-3 border focus:outline-none hover:border-gray-500 transition-[border]"
              >
                <div class="flex w-full items-center justify-center">
                  <div class="flex flex-col gap-2 items-center">
                    <svg
                      v-if="option.title == 'Own Project'"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon icon-tabler icons-tabler-outline icon-tabler-user-code"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
                      <path d="M6 21v-2a4 4 0 0 1 4 -4h3.5" />
                      <path d="M20 21l2 -2l-2 -2" />
                      <path d="M17 17l-2 2l2 2" />
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="icon icon-tabler icons-tabler-outline icon-tabler-users-group"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M10 13a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" />
                      <path d="M8 21v-1a2 2 0 0 1 2 -2h4a2 2 0 0 1 2 2v1" />
                      <path d="M15 5a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" />
                      <path d="M17 10h2a2 2 0 0 1 2 2v1" />
                      <path d="M5 5a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" />
                      <path d="M3 13v-1a2 2 0 0 1 2 -2h2" />
                    </svg>
                    <div class="text-sm font-semibold">
                      <RadioGroupLabel as="p" class="font-medium">
                        {{ option.title }}
                      </RadioGroupLabel>
                    </div>
                    <div class="text-xs text-gray-600 text-center">
                      {{ option.description }}
                    </div>
                  </div>
                </div>
              </div>
            </RadioGroupOption>
          </RadioGroup>
        </div>
        <div
          v-if="
            !hackathon.data.has_partner_projects ||
            !team.working_on_partner_project
          "
          class="mt-5"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-3">
            <FormControl type="text" label="Title" v-model="project.title" />
            <FormControl
              type="url"
              label="Repo Link"
              v-model="project.repo_link"
              description="Link your project's github repository link. Make sure the project is public."
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
                  class="icon icon-tabler icons-tabler-outline w-4 icon-tabler-brand-github"
                >
                  <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                  <path
                    d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"
                  />
                </svg>
              </template>
            </FormControl>
            <FormControl
              type="text"
              label="Short Description"
              description="A one-line description of your project."
            />
            <div class="flex flex-col gap-2">
              <h5 class="text-sm text-gray-600">Detailed Description</h5>
              <TextEditor
                :placeholder="'Write a detailed description of your project'"
                :modelValue="project.description"
                @update:modelValue="($event) => (project.description = $event)"
              />
            </div>
          </div>
        </div>
        <div v-if="team.working_on_partner_project">
          <h5 class="text-sm text-gray-600">Select Partner Project</h5>
          <RadioGroup
            v-model="team.partner_project"
            class="grid grid-cols-1 md:grid-cols-3 gap-2 my-3"
          >
            <RadioGroupOption
              as="template"
              v-for="project in partner_projects.data"
              :key="project.id"
              :value="project.name"
              v-slot="{ active, checked }"
            >
              <div
                :class="[checked ? 'bg-gray-50 border-gray-700' : 'bg-white ']"
                class="relative flex cursor-pointer rounded-sm p-4 border focus:outline-none transition-[border]"
              >
                <div class="flex w-full items-center justify-between">
                  <div class="flex flex-col gap-2 items-start">
                    <img :src="project.logo" class="h-8" />
                    <RadioGroupLabel as="p" class="text-base font-medium">
                      {{ project.project_name }}
                    </RadioGroupLabel>
                    <div class="text-sm">
                      {{ project.about }}
                    </div>
                    <a
                      :href="project.repo_link"
                      class="flex items-center gap-1 mt-3 text-xs text-gray-600 text-center hover:text-gray-800"
                      target="_blank"
                    >
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
                        class="w-4 icon icon-tabler icons-tabler-outline icon-tabler-brand-github"
                      >
                        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                        <path
                          d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"
                        />
                      </svg>
                      <span> Repo Link </span>
                    </a>
                  </div>
                </div>
              </div>
            </RadioGroupOption>
          </RadioGroup>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 place-items-end mt-6">
        <div v-if="errors" class="mb-4 w-full md:col-span-2 text-sm text-red-500" v-html="errors"></div>
        <div></div>
        <Button
          variant="solid"
          theme="green"
          class="w-full md:w-2/3 font-medium"
          label="Register"
          @click="handleRegistration"
        />
      </div>
    </div>
    <div v-else class="w-full h-screen flex justify-center align-middle">
      <LoadingIndicator class="w-8" />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import {
  createResource,
  usePageMeta,
  LoadingIndicator,
  FormControl,
  createListResource,
  Dialog,
  ErrorMessage,
} from 'frappe-ui'
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TextEditor from '@/components/TextEditor.vue'

import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'

const route = useRoute()
const router = useRouter()

usePageMeta(() => {
  return {
    title: 'Register Team',
  }
})

const attend_option = [
  {
    title: 'Remote',
    value: 0,
  },
  {
    title: 'LocalHost',
    value: 1,
  },
]

let selected_attendance = ref(attend_option[0])

const project_options = [
  {
    title: 'Own Project',
    description: 'You will work on your own project',
    value: 0,
  },
  {
    title: 'Partner Project',
    description: 'You will work on a project with a partner',
    value: 1,
  },
]

let selected_project_option = ref(project_options[0])

const team = reactive({
  team_name: '',
  wants_to_attend_locally: 0,
  localhost: '',
  working_on_partner_project: 0,
  partner_project: '',
})

const project = reactive({
  title: '',
  repo_link: '',
  short_description: '',
  description: '',
})

const hackathonId = ref(null)

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon',
  makeParams() {
    return {
      name: hackathonId.value,
    }
  },
})

const localhost = createListResource({
  doctype: 'FOSS Hackathon LocalHost',
  fields: ['*'],
  pageLength: 100,
})

const partner_projects = createListResource({
  doctype: 'FOSS Hackathon Partner Project',
  fields: ['*'],
  pageLength: 100,
})

watch(hackathon, () => {
  if (hackathon.data) {
    if (hackathon.data.has_localhosts) {
      localhost.update({
        filters: {
          parent_hackathon: hackathon.data.name,
        },
      })
      localhost.fetch()
    }
    if (hackathon.data.has_partner_projects) {
      partner_projects.update({
        filters: {
          hackathon: hackathon.data.name,
        },
      })
      partner_projects.fetch()
    }
  }
})

watch(selected_attendance, (value) => {
  team.wants_to_attend_locally = value.value
  if (value.value == 0) {
    team.localhost = ''
  }
})

watch(selected_project_option, (value) => {
  team.working_on_partner_project = value.value
  if (value.value == 0) {
    team.partner_project = ''
  }
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('id')) {
    hackathonId.value = params.get('id')
    hackathon.fetch()
  }
})

const redirectToHackathon = computed(() => {
  if (hackathon.data) {
    return `${window.location.origin}/${hackathon.data.route}`
  }
})

const show_dialog = ref(false)
const dialog_content = reactive({
  title: '',
  message: '',
})

const registrationErrors = computed(() => {
  const errors = []

  if (!team.team_name) {
    errors.push('Team Name is required')
  }

  if ( team.wants_to_attend_locally && !team.localhost) {
    errors.push('Please select a LocalHost.')
  }

  if ( team.working_on_partner_project && !team.partner_project) {
    errors.push('Please select a partner project.')
  }

  if (!team.working_on_partner_project){
    if (!project.title) {
      errors.push('Project Title is required.')
    }
    if (!project.repo_link) {
      errors.push('Project Repo Link is required.')
    }
    if (!project.description) {
      errors.push('Project Description is required.')
    }
    if (!project.short_description) {
      errors.push('Project Short Description is required.')
    }
    if(project.repo_link && !project.repo_link.includes("https://")){
      errors.push('Please enter a valid repository URL.')
    }
  }

  return errors
})

const registerForHackathon = createResource({
  url: 'fossunited.api.hackathon.register_for_hackathon',
  params: {
    hackathon: hackathon,
    team: team,
    project: project,
  },
  onSuccess(data) {
    router.push(`/my-hackathons?id=${data.team_doc.name}`)
  },
  onError(error) {
    console.log(error)
    dialog_content.title = 'Error'
    dialog_content.message = error.message
    show_dialog.value = true
  },
})

const errors = ref('')

const handleRegistration = () => {
  if (registrationErrors.value.length) {
    errors.value = registrationErrors.value.join('<br>')
    return
  }
  registerForHackathon.fetch()
}
</script>
