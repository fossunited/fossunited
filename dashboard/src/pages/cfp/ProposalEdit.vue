<template>
  <div class="flex flex-col md:flex-row">
    <SideNavbar title="Edit Proposal">
      <template #pre-nav-items>
        <div>
          <Button label="Go Back" icon-left="arrow-left" variant="ghost" @click="router.back()" />
        </div>
      </template>
      <template #post-nav-items>
        <p class="text-base text-gray-600">Edit your talk proposal</p>
      </template>
    </SideNavbar>
    <div v-if="cfpForm.data" class="w-full md:ml-[220px]">
      <SubmissionHeader :submission="submission.doc" />
      <div class="px-6 w-fit">
        <TabButtons v-model="selectedTab" :buttons="tabs" />
      </div>
      <SessionDetailForm
        v-show="selectedTab === 0"
        v-model:references="submission.doc.references"
        v-model:fields="formFields"
        :show-withdrawal="true"
        :show-title="false"
        class="border-none p-6"
      />
      <SpeakersForm
        v-show="selectedTab === 1"
        v-model:speakers="speakerFields"
        :show-title="false"
        class="border-none p-6"
      />
      <div
        class="sticky bottom-0 w-full flex flex-col-reverse md:flex-row-reverse justify-between items-end gap-2 p-4 border-t bg-white"
      >
        <Button label="Save" variant="solid" class="w-full md:w-1/3" @click="saveProposal" />
        <ErrorMessage class="w-full" :message="errorMessages" />
      </div>
    </div>
  </div>
</template>
<script setup>
import SubmissionHeader from '@/components/cfp-submission-edit/SubmissionHeader.vue'
import SideNavbar from '@/components/NewAppSidebar.vue'
import SessionDetailForm from '@/components/cfp-public/SessionDetailForm.vue'
import SpeakersForm from '@/components/cfp-public/SpeakersForm.vue'
import { createDocumentResource, createResource, TabButtons, ErrorMessage } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { useRoute, useRouter } from 'vue-router'
import {
  getProposalFormFields,
  getSpeakerFields,
  validateRequiredFields,
  validateReferences,
  validateSpeakerFields,
  getTransformedSubmissionFields,
} from '@/helpers/cfp'
import { ref, watch } from 'vue'

const route = useRoute()
const router = useRouter()
const formFields = ref([])
const speakerFields = ref([])
const selectedTab = ref(0)
const errorMessages = ref()

const tabs = [
  {
    label: 'Submission Details',
    value: 0,
    component: SessionDetailForm,
  },
  {
    label: 'Speakers',
    value: 1,
    component: SpeakersForm,
  },
]

const cfpForm = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP',
      fields: ['*'],
      filters: {
        event: submission.doc.event,
      },
    }
  },
  onSuccess() {
    mapTalkFields()
    mapToSpeakerFields()
  },
})

const submission = createDocumentResource({
  doctype: 'FOSS Event CFP Submission',
  name: route.params.id,
  fields: ['*'],
  onSuccess() {
    cfpForm.fetch()
  },
})

const mapTalkFields = () => {
  formFields.value = getProposalFormFields(cfpForm.data).value
  formFields.value.forEach((field) => {
    if (field.fieldname === 'session_categories' && submission.doc[field.fieldname]) {
      field.value = submission.doc[field.fieldname].split('\n')
    } else if (field.fieldname.startsWith('custom_question')) {
      const customAnswer = submission.doc.custom_answers.find(
        (answer) => answer.question === field.label,
      )
      field.value = customAnswer ? customAnswer.response : null
    } else {
      field.value = submission.doc[field.fieldname]
    }
  })
}

const mapToSpeakerFields = () => {
  submission.doc.speakers.forEach((speaker) => {
    let fields = getSpeakerFields()
    fields.forEach((field) => {
      if (Object.prototype.hasOwnProperty.call(speaker, field.fieldname)) {
        field.value = speaker[field.fieldname]
      }
    })
    speakerFields.value.push(fields)
  })
}

const saveProposal = () => {
  let errors = []

  errors.push(validateRequiredFields(formFields.value))
  errors.push(validateReferences(submission.doc.references))
  errors.push(validateSpeakerFields(speakerFields.value))

  // remove empty [] from errors
  errors = errors.filter((error) => error.length)

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  const transformedFields = getTransformedSubmissionFields(
    formFields.value,
    submission.doc.references,
    speakerFields.value,
  )

  submission.setValue
    .submit(transformedFields)
    .then(() => {
      errorMessages.value = ''
      toast.success('Proposal Updated Successfully!')
    })
    .catch((err) => {
      toast.error(err)
    })
}
</script>
