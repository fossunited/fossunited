<template>
  <Header />
  <div class="w-full flex flex-col items-center bg-surface-gray-1 mb-20 min-h-screen">
    <main
      v-if="cfpData.data"
      class="max-w-[800px] w-full flex flex-col gap-4 my-2 px-4"
      :aria-label="`CFP Application — ${sectionLabel}`"
    >
      <Breadcrumb :items="breadcrumb_items" />
      <FormHeader />
      <EventHeader v-if="cfpData.data.event" :event="cfpData.data.event" />

      <!-- visually-hidden live region announces step changes to screen readers -->
      <div aria-live="polite" aria-atomic="true" class="sr-only">{{ sectionLabel }}</div>

      <template v-if="cfpData.data.status == 'Live'">
        <transition
          mode="out-in"
          :enter-active-class="transitionClasses.enterActive"
          :enter-from-class="transitionClasses.enterFrom"
          :enter-to-class="transitionClasses.enterTo"
          :leave-active-class="transitionClasses.leaveActive"
          :leave-from-class="transitionClasses.leaveFrom"
          :leave-to-class="transitionClasses.leaveTo"
          @after-enter="focusSection"
        >
          <div ref="sectionContent" :key="curr_section" tabindex="-1" class="focus:outline-none">
            <GuidelineSection v-if="curr_section === 0" />
            <SessionDetailForm
              v-else-if="curr_section === 1"
              v-model:fields="proposalFormFields"
              v-model:references="proposalReferences"
            />
            <SpeakersForm
              v-else-if="curr_section === 2"
              v-model:speakers="proposalSpeakers"
              v-model:subscribe-newsletter="subscribeNewsletter"
            />
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

        <div role="alert" aria-live="assertive" aria-atomic="true">
          <ErrorMessage :message="errorMessages" />
        </div>
        <MessageBanner
          v-if="isGuestUser"
          class="justify-center gap-4 bg-surface-gray-2"
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
            :loading="isSubmitting"
            @next="nextStep"
            @back="prevStep"
            @submit="submitForm"
          />
        </div>
      </template>
      <template v-else>
        <FormClosedSection />
      </template>
    </main>
    <div v-else aria-busy="true" aria-label="Loading form">
      <LoadingIndicator />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import FormHeader from '@/components/cfp-public/FormHeader.vue'
import EventHeader from '@/components/common/EventHeader.vue'
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
import { provide, ref, watch, computed, inject, nextTick } from 'vue'
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
const sectionContent = ref(null)

const SECTION_LABELS = ['Guidelines', 'Session Details', 'Speaker Information', 'Preview & Submit']
const sectionLabel = computed(() => {
  if (curr_section.value === 'success') return 'Submission Successful'
  return `Step ${curr_section.value + 1} of ${maxSectionIndex + 1}: ${SECTION_LABELS[curr_section.value] ?? ''}`
})

const focusSection = () => {
  nextTick(() => sectionContent.value?.focus())
}

const session = inject('$session')

const isGuestUser = computed(() => {
  return !session.user
})

const inLoading = ref(true)

const proposalFormFields = ref([])
const proposalReferences = ref([])
const proposalSpeakers = ref([])
const proposalConfirmationFields = ref([])
const subscribeNewsletter = ref(false)

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

const isSubmitting = ref(false)

const newsletterSubscribe = createResource({
  url: 'fossunited.api.emailing.listmonk_subscribe',
})

const insertProposal = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'FOSS Event CFP Submission',
        linked_cfp: cfpData.data.name,
        submitted_by: session.user,
        accept_coc: proposalConfirmationFields.value.find((f) => f.fieldname === 'accept_coc')
          ?.value
          ? 1
          : 0,
        ...getTransformedSubmissionFields(
          proposalFormFields.value,
          proposalReferences.value,
          proposalSpeakers.value,
        ),
      },
    }
  },
  onSuccess() {
    isSubmitting.value = false
    curr_section.value = 'success'
    toast.success('Proposal submitted successfully!')
    if (subscribeNewsletter.value) {
      for (const speaker of proposalSpeakers.value) {
        const email = speaker.find((f) => f.fieldname === 'email')?.value
        const name = speaker.find((f) => f.fieldname === 'speaker_name')?.value || ''
        if (email) newsletterSubscribe.fetch({ email, name })
      }
    }
  },
  onError(err) {
    isSubmitting.value = false
    errorMessages.value = err.message
    showError(err, 'Error submitting the proposal')
  },
})

function submitForm() {
  if (isSubmitting.value) return
  isSubmitting.value = true

  let errors = []
  if (curr_section.value == 3) {
    errors = errors.concat(validateRequiredFields(proposalConfirmationFields.value))
  }
  if (errors.length) {
    isSubmitting.value = false
    errorMessages.value = errors.join('\n\n')
    return
  }
  errorMessages.value = ''

  insertProposal.fetch()
}
</script>
