<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 flex flex-col gap-8">
    <div class="flex flex-col md:flex-row justify-between gap-2">
      <div class="text-xl font-medium">Create CFP</div>
      <Button size="md" label="Create" variant="solid" @click="createCfpForm" />
    </div>
    <div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-8">
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.allow_cfp_edit"
            type="checkbox"
            label="Allow Proposal Edit"
            description=""
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >Allow users to edit their proposals after submission.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.anonymise_proposals"
            type="checkbox"
            label="Anonymise Proposals?"
            description=""
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >The proposals will not show the name of the proposer.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.hide_review"
            type="checkbox"
            label="Hide Reviews"
            description=""
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >Hide the reviews section from the public proposal page.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.hide_contact_info"
            type="checkbox"
            label="Hide Contact Info Field"
            description=""
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >Removes the optional "Contact Info" field from the speaker form.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.require_speaker_photo"
            type="checkbox"
            label="Require Speaker Photo"
            description=""
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >If unchecked, speakers can submit without uploading a photo.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp_doc.deadline"
            type="datetime-local"
            label="Submission Deadline"
            size="md"
          />
          <span class="text-sm text-ink-gray-5"
            >The form auto-closes once this date and time passes. Leave empty to keep it open and
            close the form manually with Publish/Unpublish.</span
          >
        </div>
        <div class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <TextEditor
            large
            placeholder="This will be shown on the CFP form."
            label="CFP Form Description"
            :model-value="cfp_doc.cfp_form_description"
            @update:model-value="($event) => (cfp_doc.cfp_form_description = $event)"
          />
          <span class="text-sm text-ink-gray-5"
            >Shown as the guideline step for applicants. Leave empty to show the foundation's
            default guidelines instead. If filled, this replaces the default entirely — include
            everything applicants need, not just an addition to it.</span
          >
        </div>
        <div class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <span class="text-base text-ink-gray-5">Allowed Session Types</span>
          <div class="grid grid-cols-2 gap-2">
            <FormControl
              v-for="type in SESSION_TYPES"
              :key="type"
              type="checkbox"
              :label="type"
              :model-value="isSessionTypeAllowed(cfp_doc.allowed_session_types, type)"
              @update:model-value="(val) => toggleSessionType(type, val)"
              size="md"
            />
          </div>
          <span class="text-sm text-ink-gray-5"
            >Restrict which session types applicants can choose from. Leave all checked to allow
            every type.</span
          >
        </div>
        <FormControl
          class="col-span-1 md:col-span-2"
          v-model="cfp_doc.override_session_categories"
          type="textarea"
          label="Override Session Categories"
          description='One category per line. Leave empty to use FOSS United&#39;s default category list. Include "Other" as one of the lines to let proposers type in their own custom category.'
          size="md"
        />
      </div>
    </div>
    <div>
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Standard Fields</div>
      <div class="py-4 grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        <FormControl
          v-for="(field, index) in standard_fields"
          :key="index"
          :size="'md'"
          :disabled="true"
          :type="field.type"
          :label="field.label"
          :description="field.description"
        />
      </div>
    </div>
    <div>
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Custom Fields</div>
      <div class="flex flex-col gap-3 mt-4">
        <FormControl
          v-model="cfp_doc.has_public_custom_responses"
          type="checkbox"
          label="Public Custom Responses"
          size="md"
        />
        <span class="text-sm text-ink-gray-5"
          >Show answers to these custom questions publicly on the proposal page. Be careful: do not
          make responses public if any question collects sensitive data such as phone numbers or
          email addresses.</span
        >
        <span class="text-sm text-ink-gray-5"
          >Fields of type "Check" appear as confirmation checkboxes on the final review step,
          instead of on the submission form.</span
        >
      </div>
      <Button
        class="mt-3"
        size="md"
        icon-left="plus"
        label="Add Custom Field"
        @click="() => (show_dialog = true)"
      />
      <ListView
        class="mt-4"
        :columns="[
          { label: 'Question', key: 'question' },
          { label: 'Type', key: 'type' },
        ]"
        :rows="cfp_doc.cfp_custom_questions"
        row-key="idx"
        :options="{
          selectable: false,
          emptyState: {
            title: 'No Custom Fields',
            description: 'No custom fields have been added yet.',
          },
          onRowClick: (row) => handleCustomRowEdit(row),
        }"
      />
    </div>
    <Dialog
      v-model="show_dialog"
      title="Add Custom Field"
      size="md"
      :options="{
        title: 'Add Custom Field',
      }"
    >
      <template #body-content>
        <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <FormControl
            v-model="custom_field.question"
            class="col-span-2"
            size="md"
            type="text"
            label="Question"
            description="The question you want to ask the attendees."
          />
          <div>
            <FormControl
              v-model="custom_field.is_mandatory"
              size="md"
              type="checkbox"
              label="Is Mandatory"
              description="Whether the question is mandatory or not."
            />
            <div class="text-sm text-ink-gray-5">Whether the question is mandatory or not.</div>
          </div>
          <FormControl
            v-model="custom_field.type"
            size="md"
            type="select"
            label="Type"
            :options="[
              { label: 'Data', value: 'Data' },
              { label: 'Select', value: 'Select' },
              { label: 'Long Text', value: 'Long Text' },
              { label: 'Text Editor', value: 'Text Editor' },
              { label: 'Check', value: 'Check' },
              { label: 'Radio Group', value: 'Radio Group' },
            ]"
            description="The type of question you want to ask."
          />
          <FormControl
            v-if="custom_field.type === 'Select'"
            v-model="custom_field.options"
            class="col-span-2"
            size="md"
            type="textarea"
            label="Options"
            description="Options for the select field. Enter each option on a new line."
          />
          <FormControl
            v-model="custom_field.description"
            class="col-span-2"
            size="md"
            type="textarea"
            label="Description"
            description="Description for the question."
          />
        </div>
      </template>
      <template #actions>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button v-if="inCustomEdit" label="Save" variant="solid" @click="updateCustomField" />
          <Button v-else label="Add Field" variant="solid" @click="addCustomField" />
          <Button label="Cancel" theme="red" @click="() => (show_dialog = false)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>
<script setup>
import { createDocumentResource, FormControl, ListView, Dialog, createResource } from 'frappe-ui'
import { reactive, ref, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import TextEditor from '@/components/ui/TextEditor.vue'
import { SESSION_TYPES, isSessionTypeAllowed, getUpdatedAllowedSessionTypes } from '@/helpers/cfp'

const route = useRoute()
const emit = defineEmits(['cfpCreated'])

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const standard_fields = [
  {
    label: 'Name',
    description: 'Full Name of the attendee',
    type: 'text',
  },
  {
    label: 'Email',
    description: 'Email of the attendee',
    type: 'select',
  },
  {
    label: 'Picture (URL)',
    description: 'URL for a publicly hosted photo',
    type: 'url',
  },
  {
    label: 'Designation',
    description: 'Designation of the attendee',
    type: 'text',
  },
  {
    label: 'Organization',
    description: 'Organization of the attendee',
    type: 'text',
  },
  {
    label: 'Speaker Bio',
    description: 'Short bio of the speaker',
    type: 'textarea',
  },
  {
    label: 'Is this your first talk?',
    type: 'select',
  },
  {
    label: 'Session Type',
    description: 'Type of session attendee is proposing',
    type: 'select',
  },
  {
    label: 'Session Title',
    description: 'Title of the session',
    type: 'text',
  },
  {
    label: 'Session Reference',
    description: 'Link relevant references for the talk.',
    type: 'url',
  },
  {
    label: 'Session Description',
    description: 'Description of the session',
    type: 'textarea',
  },
]

let cfp_doc = reactive({
  doctype: 'FOSS Event CFP',
  event: route.params.id,
  anonymise_proposals: 1,
  allow_cfp_edit: 0,
  allowed_session_types: '',
  override_session_categories: '',
  hide_contact_info: 0,
  require_speaker_photo: 1,
  deadline: '',
  hide_review: 1,
  has_public_custom_responses: 0,
  cfp_form_description: '',
  cfp_custom_questions: [],
})

const toggleSessionType = (type, checked) => {
  cfp_doc.allowed_session_types = getUpdatedAllowedSessionTypes(
    cfp_doc.allowed_session_types,
    type,
    checked,
  )
}

let custom_field = reactive({
  idx: 1,
  question: '',
  type: '',
  is_mandatory: 0,
  options: '',
  description: '',
})
let show_dialog = ref(false)

const addCustomField = () => {
  cfp_doc.cfp_custom_questions.push(custom_field)
  custom_field = {
    idx: custom_field.idx + 1,
    question: '',
    type: '',
    is_mandatory: 0,
    options: '',
    description: '',
  }
  show_dialog.value = false
}

let inCustomEdit = ref(false)
const handleCustomRowEdit = (row) => {
  inCustomEdit.value = true
  custom_field = row
  show_dialog.value = true
}
const updateCustomField = () => {
  const index = cfp_doc.cfp_custom_questions.findIndex((field) => field.idx === custom_field.idx)
  cfp_doc.cfp_custom_questions[index] = custom_field
  show_dialog.value = false
  inCustomEdit.value = false
  custom_field = {
    idx: custom_field.idx + 1,
    question: '',
    type: '',
    is_mandatory: 0,
    options: '',
    description: '',
  }
}

const createCfpForm = () => {
  let cfp = createResource({
    url: 'frappe.client.insert',
    params: {
      doc: cfp_doc,
    },
  })
  cfp
    .submit()
    .then((result) => {
      toast.success('CFP Form Created Successfully.')
      emit('cfpCreated')
    })
    .catch((error) => {
      toast.error('Error creating CFP Form.', {
        description: error.message,
      })
    })
}
</script>
