<template>
  <Header />
  <Dialog
    v-model="show_dialog"
    class="z-50"
    :options="{
      title: dialog_content.title,
      message: dialog_content.message,
    }"
  />
  <div class="w-full flex justify-center">
    <div v-if="hackathon.data" class="container p-8">
      <div class="flex gap-2 mb-10 items-center">
        <a :href="redirectToHackathon" class="font-semibold text-base hover:underline">{{
          hackathon.data.hackathon_name
        }}</a>
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
      <div class="mt-2" v-html="hackathon.data.registration_description"></div>
      <hr class="my-4" />

      <!-- DETAILS -->
      <div class="w-full">
        <h3 class="text-lg font-semibold">Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-3">
          <FormControl
            v-model="participant.full_name"
            type="text"
            label="Full Name &ast;"
            placeholder="John Doe"
          />
          <FormControl
            v-model="participant.email"
            type="email"
            label="Email &ast;"
            placeholder="john@fossunited.org"
          />
          <FormControl v-model="participant.is_student" type="checkbox" label="I am a student" />
          <FormControl
            v-model="participant.organization"
            type="text"
            label="Organization / Institute &ast;"
          />
        </div>
        <div class="mt-6">
          <h5 class="text-base font-medium text-gray-800">Link your Git Profile &ast;</h5>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2">
          <FormControl
            v-model="participant.git_profile"
            type="url"
            placeholder="https://github.com/username"
            class="mt-2"
          >
          </FormControl>
        </div>
        <div v-if="localhost.data" class="mt-6">
          <h5 class="text-base font-medium text-gray-800">How will you participate?</h5>
          <RadioGroup
            v-model="selected_attendance"
            class="grid sm:grid-cols-3 lg:grid-cols-5 gap-2 my-3"
          >
            <RadioGroupOption
              v-for="option in attend_option"
              :key="option.value"
              v-slot="{ checked }"
              as="template"
              :value="option"
            >
              <div
                :class="[checked ? 'bg-gray-50 border-gray-700' : 'bg-white ']"
                class="relative flex cursor-pointer rounded-sm px-5 py-3 border focus:outline-none hover:border-gray-500 transition-[border]"
              >
                <div class="flex w-full items-center justify-center">
                  <div class="flex flex-col gap-2 items-center">
                    <svg
                      v-if="option.title == 'Virtually'"
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
          <div v-if="selected_attendance.value == 1" class="grid grid-cols-1 md:grid-cols-2">
            <FormControl
              v-model="participant.localhost"
              type="select"
              label="Select Location &ast;"
              placeholder="-- Select In-Person Venue --"
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
              Please note that attendance at offline venues is limited by seat availability. Our
              team will review your application to attend the hackathon.<br />
              If there are not enough seats available, your application to attend in person may be
              <b>declined</b>, and you may need to participate remotely.
            </p>
          </div>
        </div>
      </div>
      <ErrorMessage v-if="errorsMessage" class="m-2 mt-5" :message="errorsMessage" />
      <div class="flex flex-row-reverse mt-6">
        <Button
          variant="solid"
          theme="green"
          class="w-full md:w-2/5 font-medium"
          label="Register"
          :loading="registerForHackathon.loading"
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
    title: 'Virtually',
    value: 0,
  },
  {
    title: 'In-Person',
    value: 1,
  },
]

let selected_attendance = ref(attend_option[0])

let participant = reactive({
  user_profile: '',
  full_name: '',
  email: '',
  user: '',
  git_profile: '',
  is_student: 0,
  organization: '',
  wants_to_attend_locally: '',
  localhost: '',
})

const hackathonId = ref(null)

const alreadyParticipant = createResource({
  url: 'frappe.client.get_count',
  onSuccess(data) {
    if (data > 0) {
      dialog_content.title = 'Already Registered'
      dialog_content.message = 'You have already registered for this hackathon. Redirecting...'
      show_dialog.value = true
      setTimeout(() => {
        router.push({
          name: 'InitialRegister',
          params: {
            permalink: hackathon.data.permalink,
          },
        })
      }, 3000)
    }
  },
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon',
  makeParams() {
    return {
      name: hackathonId.value,
    }
  },
  onSuccess(data) {
    alreadyParticipant.update({
      params: {
        doctype: 'FOSS Hackathon Participant',
        filters: {
          hackathon: data.name,
          user: session.user,
        },
      },
    })
    alreadyParticipant.fetch()
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
          is_accepting_attendees: 1,
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
  onSuccess(data) {
    participant.user_profile = data.name
    participant.full_name = data.full_name
    participant.email = data.user
    participant.git_profile = data.github
  },
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('id')) {
    hackathonId.value = params.get('id')
    hackathon.fetch()
  }
  if (session.user != 'Administrator' && session.user != 'Guest') {
    participant.user = session.user
    user_profile.update({
      params: {
        email: session.user,
      },
    })
    user_profile.fetch()
  }
})

const redirectToHackathon = computed(() => {
  if (hackathon.data) {
    return `${window.location.origin}/${hackathon.data.route}`
  }
  return window.location.origin
})

const show_dialog = ref(false)
const dialog_content = reactive({
  title: '',
  message: '',
})

const registrationErrors = computed(() => {
  const errors = []

  if (!participant.full_name) {
    errors.push('Name is required.')
  }
  if (!participant.email) {
    errors.push('Email is required.')
  }
  if (!participant.organization) {
    errors.push('Organization / Institute is required.')
  }
  if (!participant.git_profile) {
    errors.push('Git Profile is required')
  }
  if (participant.git_profile && !participant.git_profile.startsWith('https://')) {
    errors.push('Enter a valid URL')
  }

  if (participant.wants_to_attend_locally && !participant.localhost) {
    errors.push('Please select an In-Person location.')
  }

  return errors
})

const registerForHackathon = createResource({
  url: 'fossunited.api.hackathon.create_participant',
  params: {
    hackathon: hackathon,
    participant: participant,
  },
  onSuccess(data) {
    router.push({
      name: 'InitialRegister',
      params: {
        permalink: hackathon.data.permalink,
      },
    })
  },
  onError(error) {
    console.error()
    dialog_content.title = 'Error'
    dialog_content.message = error.message
    show_dialog.value = true
  },
})

const errorsMessage = ref('')

const handleRegistration = () => {
  if (registrationErrors.value.length) {
    errorsMessage.value = registrationErrors.value.join(', ')
    return
  } else {
    errorsMessage.value = null
  }
  registerForHackathon.fetch()
}
</script>
