<template>
  <Header />
  <Dialog
    v-model="show_dialog"
    :options="{
      title: dialog_content.title,
      message: dialog_content.message,
    }"
  />
  <div class="w-full flex justify-center">
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

      <!-- DETAILS -->
      <div class="w-full">
        <h3 class="text-lg font-semibold">Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-3">
          <FormControl
            type="text"
            label="Full Name"
            placeholder="John Doe"
            v-model="participant.full_name"
          />
          <FormControl
            type="email"
            label="Email"
            placeholder="john@fossunited.org"
            v-model="participant.email"
          />
          <FormControl
            type="checkbox"
            label="I am a student"
            v-model="participant.is_student"
          />
          <FormControl
            type="text"
            label="Organization / Institute"
            v-model="participant.organization"
          />
        </div>
        <div class="mt-6">
          <h5 class="text-base font-medium text-gray-800">
            Select your platform
          </h5>
          <RadioGroup
            v-model="selected_platform"
            class="grid sm:grid-cols-3 lg:grid-cols-5 gap-2 my-3"
          >
            <RadioGroupOption
              as="template"
              v-for="option in platform_options"
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
                      v-if="option.value == 'github'"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="w-5 icon icon-tabler icons-tabler-outline icon-tabler-brand-github"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path
                        d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"
                      />
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
                      class="w-5 icon icon-tabler icons-tabler-outline icon-tabler-brand-gitlab"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                      <path d="M21 14l-9 7l-9 -7l3 -11l3 7h6l3 -7z" />
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
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2">
          <FormControl v-if="selected_platform.value==='github'" type="url" label="Github" placeholder="https://github.com/example-username" v-model="participant.github">
          </FormControl>
          <FormControl v-else type="url" label="Gitlab" placeholder="https://gitlab.com/example-username" v-model="participant.gitlab">
          </FormControl>
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
              v-model="participant.localhost"
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
            class="flex flex-col items-center sm:flex-row gap-3 bg-yellow-50 w-full p-4 text-sm rounded-sm my-4 text-yellow-700 outline-2 outline-dashed"
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
              class="w-7 shrink-0 stroke-yellow-700 icon icon-tabler icons-tabler-outline icon-tabler-alert-circle"
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
      </div>
      <ErrorMessage
        v-if="errorsMessage"
        class="m-2 mt-5"
        :message="errorsMessage"
      />
      <div class="grid grid-cols-1 md:grid-cols-2 place-items-end mt-6">
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
import { ref, onMounted, computed, reactive, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'

let session = inject('$session')

const route = useRoute()
const router = useRouter()

usePageMeta(() => {
  return {
    title: 'Register For Hackathon',
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

let participant = reactive({
  user_profile: '',
  full_name: '',
  email: '',
  github: '',
  gitlab: '',
  is_student: 0,
  organization: '',
  wants_to_attend_locally: '',
  localhost: '',
})

const platform_options = [
  {
    title: 'GitHub',
    value: 'github',
  },
  {
    title: 'GitLab',
    value: 'gitlab',
  },
]
let selected_platform = ref(platform_options[0])

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
  }
})

watch(selected_attendance, (value) => {
  participant.wants_to_attend_locally = value.value
  if (value.value == 0) {
    participant.localhost = ''
  }
})

let user_profile = createResource({
  url: 'fossunited.fossunited.utils.get_foss_profile',
  onSuccess(data){
    participant.user_profile = data.name
    participant.full_name = data.full_name
    participant.email = data.user
    participant.github = data.github
  }
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('id')) {
    hackathonId.value = params.get('id')
    hackathon.fetch()
  }
  if(session.user != 'Administrator' && session.user != 'Guest'){
    user_profile.update({
      params:{
        email: session.user
      }
    })
    user_profile.fetch()
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

  if (!participant.full_name){
    errors.push("Name is required.")
  }
  if(!participant.email){
    errors.push("Email is required.")
  }
  if(!participant.organization){
    errors.push("Organization / Institute is required.")
  }
  if( selected_platform.value.value == 'github' && !participant.github){
    errors.push("GitHub Profile is required")
  }
  if( selected_platform.value.value == 'github' && participant.github){
    if (!participant.github.startsWith('https://github.com/')){
      errors.push("Enter a valid GitHub URL")
    }
  }
  if( selected_platform.value.value == 'gitlab' && !participant.gitlab){
    errors.push("GitHub Profile is required")
  }
  if( selected_platform.value.value == 'gitlab' && participant.gitlab){
    if (!participant.gitlab.startsWith('https://gitlab.com/')){
      errors.push("Enter a valid GitLab URL")
    }
  }

  if(participant.wants_to_attend_locally && !participant.localhost){
    errors.push("Please select a LocalHost.")
  }

  return errors
})

const registerForHackathon = createResource({
  url: 'fossunited.api.hackathon.create_participant',
  params:{
    hackathon: hackathon,
    participant: participant,
  },
  onSuccess(data){
    router.push(`/my-hackathons`)
  },
  onError(error){
    console.error();
    dialog_content.title= 'Error'
    dialog_content.message = error.message
    show_dialog.value = true
  }
})

const errorsMessage = ref('')

const handleRegistration = () => {
  if (registrationErrors.value.length) {
    errorsMessage.value = registrationErrors.value.join(', ')
    return
  }else{
    errorsMessage.value = null
  }
  registerForHackathon.fetch()
}
</script>
