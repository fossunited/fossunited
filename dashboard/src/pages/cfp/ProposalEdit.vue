<template>
  <div class="flex flex-col md:flex-row">
    <SideNavbar :menu-items="sidebarMenuItems" title="Edit Proposal" />
    <div v-if="cfpForm.data" class="flex-1 min-w-0">
      <SubmissionHeader :submission="submission.doc" :readonly="!canEdit" />
      <div v-if="canEditProposal.data !== undefined" class="px-6 pt-4 pb-4">
        <div
          v-if="canEdit"
          class="rounded border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-base text-ink-gray-7"
        >
          You can edit your proposal while the CFP is open.
        </div>
        <div
          v-else
          class="rounded border border-outline-red-2 bg-surface-red-1 px-4 py-3 text-base text-ink-red-6"
        >
          The CFP is closed. This proposal is now read-only.
        </div>
      </div>
      <div class="px-6 w-fit">
        <TabButtons v-model="selectedTab" :buttons="tabs" />
      </div>
      <div
        :class="{ 'pointer-events-none opacity-60 select-none': !canEdit }"
        :aria-disabled="!canEdit"
      >
        <SessionDetailForm
          v-show="selectedTab === 0"
          v-model:references="submission.doc.references"
          v-model:fields="formFields"
          :show-title="false"
          class="border-none p-6"
        />
        <SpeakersForm
          v-show="selectedTab === 1"
          v-model:speakers="speakerFields"
          :show-title="false"
          class="border-none p-6"
        />
      </div>
      <ActionsForm v-show="selectedTab === 2" v-model:cfpid="route.params.id" />
      <div
        v-if="selectedTab !== 2"
        class="sticky bottom-0 w-full flex flex-col-reverse md:flex-row-reverse justify-between items-end gap-2 p-4 border-t bg-surface-white"
      >
        <Button
          v-if="canEdit"
          label="Save"
          variant="solid"
          class="w-full md:w-1/3"
          @click="saveProposal"
        />
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
import ActionsForm from '@/components/cfp-public/ActionsForm.vue'
import { createDocumentResource, createResource, TabButtons, ErrorMessage } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { useRoute } from 'vue-router'
import {
  getProposalFormFields,
  getSpeakerFields,
  validateRequiredFields,
  validateReferences,
  validateSpeakerFields,
  getTransformedSubmissionFields,
} from '@/helpers/cfp'
import { ref, provide, computed, inject, watch } from 'vue'

const route = useRoute()
const session = inject('$session')
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
  {
    label: 'Actions',
    value: 2,
    component: ActionsForm,
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

const canEditProposal = createResource({
  url: 'fossunited.api.cfp.can_edit_proposal',
  makeParams() {
    return { cfp_submission: route.params.id }
  },
})

const canEdit = computed(() => canEditProposal.data ?? true)

const proposals = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      fields: ['name', 'talk_title', 'event_name', 'creation'],
      orderBy: 'creation desc',
      limit_page_length: 999,
      or_filters: { email: session.user, submitted_by: session.user },
    }
  },
  auto: true,
})

const sidebarMenuItems = computed(() => {
  const items = [
    { items: [{ icon: 'arrow-left', label: 'My Proposals', route: '/my-proposals' }] },
  ]

  if (proposals.data?.length) {
    items.push({
      parent_label: 'My Proposals',
      items: proposals.data.map((p) => ({
        label: p.talk_title,
        route: `/my-proposals/edit/${p.name}`,
      })),
    })
  }

  return items
})

const submission = createDocumentResource({
  doctype: 'FOSS Event CFP Submission',
  name: route.params.id,
  fields: ['*'],
})

provide('submission', submission)

// createDocumentResource is globally cached; on remount it may return a cached
// instance whose onSuccess closure is bound to a destroyed component. Drive the
// dependent fetches from a watcher local to this instance instead. Fire only on
// the first load (falsy -> truthy) so a save (which mutates doc) does not
// re-trigger mapping and duplicate speakers.
watch(
  () => submission.doc,
  (doc, prevDoc) => {
    if (doc && !prevDoc) {
      cfpForm.fetch()
      canEditProposal.fetch()
    }
  },
  { immediate: true },
)

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
  speakerFields.value = []
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
    toast.error(errorMessages.value)
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
      toast.error('Failed to update your proposal', {
        description: err.message,
      })
    })
}
</script>
