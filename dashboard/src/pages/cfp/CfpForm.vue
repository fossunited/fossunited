<template>
  <Header />
  <div class="w-full flex flex-col items-center bg-surface-gray-1 mb-20 min-h-screen">
    <div v-if="cfpData.data" class="max-w-[800px] w-full flex flex-col gap-6 md:gap-10 my-4 px-4">
      <Breadcrumb :items="breadcrumb_items" />
      <FormHeader />
      <EventHeader />
      <template v-if="cfpData.data.status == 'Live'">
        <transition
          mode="out-in"
          :enter-active-class="transitionClasses.enterActive"
          :enter-from-class="transitionClasses.enterFrom"
          :enter-to-class="transitionClasses.enterTo"
          :leave-active-class="transitionClasses.leaveActive"
          :leave-from-class="transitionClasses.leaveFrom"
          :leave-to-class="transitionClasses.leaveTo"
        >
          <div :key="curr_section">
            <GuidelineSection v-if="curr_section === 0" />
            <SessionDetailForm
              v-else-if="curr_section === 1"
              v-model:fields="proposalFormFields"
              v-model:references="proposalReferences"
            />
            <SpeakersForm v-else-if="curr_section === 2" v-model:speakers="proposalSpeakers" />
            <PreviewSubmission
              v-else-if="curr_section === 3"
              v-model:confirmation-fields="proposalConfirmationFields"
              :proposal-fields="proposalFormFields"
              :proposal-references="proposalReferences"
              :proposal-speakers="proposalSpeakers"
            />
            <SubmissionSuccessView v-else-if="curr_section === 'success'" />
          </div>
        </transition>

        <ErrorMessage :message="errorMessages" />
        <MessageBanner
          v-if="isGuestUser"
          class="justify-center !text-base gap-4 bg-surface-gray-2"
          variant="subtle"
          message="Please login to submit your proposal."
        >
          <template #suffix>
            <Button
              label="Log In"
              variant="outline"
              :link="createAbsoluteUrlFromRoute(`login?redirect=/dashboard${$route.fullPath}`)"
            />
          </template>
        </MessageBanner>
        <div v-else>
          <StepButtons
            v-if="curr_section !== 'success'"
            :is-first-step="curr_section === 0"
            :is-last-step="curr_section === maxSectionIndex"
            @next="nextStep"
            @back="prevStep"
            @submit="submitForm"
          />
        </div>
      </template>
      <template v-else>
        <FormClosedSection />
      </template>
    </div>
    <div v-else>
      <LoadingIndicator />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import FormHeader from '@/components/cfp-public/FormHeader.vue'
import EventHeader from '@/components/cfp-public/EventHeader.vue'
import GuidelineSection from '@/components/cfp-public/GuidelineSection.vue'
import SessionDetailForm from '@/components/cfp-public/SessionDetailForm.vue'
import SpeakersForm from '@/components/cfp-public/SpeakersForm.vue'
import StepButtons from '@/components/cfp-public/StepButtons.vue'
import FormClosedSection from '@/components/cfp-public/FormClosedSection.vue'
import SubmissionSuccessView from '@/components/cfp-public/SubmissionSuccessView.vue'
import PreviewSubmission from '@/components/cfp-public/PreviewSubmission.vue'
import MessageBanner from '@/components/ui/MessageBanner.vue'
import { createResource, LoadingIndicator, usePageMeta, ErrorMessage } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { provide, ref, watch, computed, inject } from 'vue'
import {
  getProposalFormFields,
  getReferenceItemSchema,
  getSpeakerFields,
  getSubmissionConfirmationFields,
  validateRequiredFields,
  validateReferences,
  validateSpeakerFields,
  getTransformedSubmissionFields,
} from '@/helpers/cfp'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { toast } from 'vue-sonner'

const curr_section = ref(0)
const maxSectionIndex = 3

const session = inject('$session')

const isGuestUser = computed(() => {
  return !session.user
})

const inLoading = ref(true)

const proposalFormFields = ref([])
const proposalReferences = ref([])
const proposalSpeakers = ref([])
const proposalConfirmationFields = ref([])

proposalReferences.value.push(getReferenceItemSchema())
proposalSpeakers.value.push(getSpeakerFields())
proposalConfirmationFields.value = getSubmissionConfirmationFields()

const errorMessages = ref('')

const route = useRoute()
const cfpData = createResource({
  url: 'fossunited.api.cfp.get_cfp_from_route',
  makeParams() {
    return {
      route: route.params.route,
    }
  },
  auto: true,
  onSuccess(data) {
    if (data) {
      proposalFormFields.value = getProposalFormFields(data).value
    }
  },
})

provide('$cfpData', cfpData)

usePageMeta(() => {
  return {
    title: 'Apply CFP | ' + cfpData.data?.event_name,
  }
})

const breadcrumb_items = ref([
  {
    label: cfpData.data?.event_name,
    link: `/c/${route.params.route}`,
  },
  {
    label: 'Call For Proposals',
  },
  {
    label: 'Apply',
  },
])

watch(
  () => cfpData.data,
  (newData) => {
    if (newData) {
      breadcrumb_items.value[0].label = newData.event_name
    }
  },
  { deep: true },
)

const transitionDirection = ref('next')
// Dynamically compute transition classes based on direction
const transitionClasses = computed(() => {
  if (transitionDirection.value === 'next') {
    // New component comes from right, old component leaves to left
    return {
      enterActive: 'transition ease-out duration-300',
      enterFrom: 'opacity-0 transform translate-x-1/4',
      enterTo: 'opacity-100 transform translate-x-0',
      leaveActive: 'transition ease-in duration-300',
      leaveFrom: 'opacity-100 transform translate-x-0',
      leaveTo: 'opacity-0 transform -translate-x-1/4',
    }
  } else if (transitionDirection.value === 'back') {
    // New component comes from left, old component leaves to right
    return {
      enterActive: 'transition ease-out duration-300',
      enterFrom: 'opacity-0 transform -translate-x-1/4',
      enterTo: 'opacity-100 transform translate-x-0',
      leaveActive: 'transition ease-in duration-300',
      leaveFrom: 'opacity-100 transform translate-x-0',
      leaveTo: 'opacity-0 transform translate-x-1/4',
    }
  }
  return {}
})

// Navigation functions
function nextStep() {
  errorMessages.value = ''

  let errors = []

  if (curr_section.value == 1) {
    errors = errors.concat(validateRequiredFields(proposalFormFields.value))
    errors = errors.concat(validateReferences(proposalReferences.value))
  }

  if (curr_section.value == 2) {
    const speakerErrors = validateSpeakerFields(proposalSpeakers.value)
    if (speakerErrors.length) {
      errors = errors.concat(speakerErrors) // Flattening the array
    }
  }

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  if (curr_section.value < maxSectionIndex) {
    transitionDirection.value = 'next'
    curr_section.value++
  }
}

function prevStep() {
  errorMessages.value = ''
  if (curr_section.value > 0) {
    transitionDirection.value = 'back'
    curr_section.value--
  }
}

function submitForm() {
  let errors = []

  if (curr_section.value == 3) {
    errors = errors.concat(validateRequiredFields(proposalConfirmationFields.value))
  }

  if (errors.length) {
    errorMessages.value = errors.join('\n\n') // Each error on a new line
    return
  }

  let transformedFields = getTransformedSubmissionFields(
    proposalFormFields.value,
    proposalReferences.value,
    proposalSpeakers.value,
  )
  errorMessages.value = ''

  createResource({
    url: 'frappe.client.insert',
    makeParams() {
      return {
        doc: {
          doctype: 'FOSS Event CFP Submission',
          linked_cfp: cfpData.data.name,
          submitted_by: session.user,
          ...transformedFields,
        },
      }
    },
    onSuccess() {
      curr_section.value = 'success'
      toast.success('Proposal submitted successfully!')
    },
    onError(err) {
      errorMessages.value = err.message
      toast.error('Error submitting the proposal: ' + err.message)
    },
  }).fetch()
}
</script>
