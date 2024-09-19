<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: inCreateMode ? 'Create Custom Field' : 'Edit Custom Field',
      width: 'md',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl v-model="question.label" label="Question &ast;" />
        <FormControl
          v-model="question.field_type"
          label="Field Type &ast;"
          type="select"
          :options="[
            { label: 'Data', value: 'Data' },
            { label: 'Select', value: 'Select' },
            { label: 'Int', value: 'Int' },
          ]"
        />
        <div class="my-1 flex flex-col gap-1">
          <FormControl v-model="question.mandatory" label="Is Mandatory" type="checkbox" />
          <small class="text-gray-600">Whether the question is mandatory or not.</small>
        </div>
        <FormControl
          v-model="question.field_name"
          label="Field Name &ast;"
          description="The name of the field."
        />
        <FormControl
          v-if="question.field_type === 'Select'"
          v-model="question.options"
          type="textarea"
          label="Options"
          description="Options for the select field. Enter each option on a new line."
        />
      </div>
      <ErrorMessage :message="errorMessages" />
    </template>
    <template #actions>
      <div class="flex gap-2 items-center">
        <Button
          v-if="!inCreateMode"
          class="w-fit px-2"
          icon="trash"
          theme="red"
          @click="handleDelete"
        />
        <Button class="w-full" label="Cancel" @click="showDialog = false" />
        <Button
          v-if="inCreateMode"
          class="w-full"
          variant="solid"
          label="Create"
          @click="handleCreate"
        />
        <Button v-else class="w-full" variant="solid" label="Save" @click="handleSave" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { defineProps, defineModel, watch, reactive, ref } from 'vue'
import { Dialog, FormControl, ErrorMessage, createResource } from 'frappe-ui'
import { toast } from 'vue-sonner'

const props = defineProps({
  event: {
    type: Object,
    default: null,
  },
  inCreateMode: {
    type: Boolean,
    default: false,
  },
  row: {
    type: Object,
    default: {},
  },
})

const showDialog = defineModel()

const question = reactive({
  label: '',
  field_type: '',
  mandatory: false,
  field_name: '',
  options: '',
})

watch(
  () => props.row,
  (row) => {
    question.label = row.label
    question.field_type = row.field_type
    question.mandatory = row.mandatory
    question.field_name = row.field_name
    question.options = row.options
  },
  { immediate: true },
)

const errorMessages = ref('')

const validateFields = () => {
  const errors = []

  if (!question.label) {
    errors.push('Question is required.')
  }
  if (!question.field_type) {
    errors.push('Field Type is required.')
  }
  if (!question.field_name) {
    errors.push('Field Name is required.')
  }
  if (question.field_type === 'Select' && !question.options) {
    errors.push('Options are required for Select field type.')
  }

  return errors
}

const createCustomField = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'FOSS Event Field',
        label: question.label,
        field_type: question.field_type,
        mandatory: question.mandatory,
        field_name: question.field_name,
        options: question.options,
        parent: props.event.data.name,
        parenttype: 'FOSS Chapter Event',
        parentfield: 'custom_fields',
      },
    }
  },
  onSuccess() {
    props.event.fetch()
    toast.success('Custom field created successfully')
    showDialog.value = false
  },
  onError(error) {
    errorMessages.value = error.message
  },
})

const updateCustomField = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Event Field',
      name: props.row.name,
      fieldname: {
        label: question.label,
        field_type: question.field_type,
        mandatory: question.mandatory,
        field_name: question.field_name,
        options: question.options,
      },
    }
  },
  onSuccess() {
    props.event.fetch()
    toast.success('Custom field updated successfully')
    showDialog.value = false
  },
  onError(error) {
    errorMessages.value = error.message
  },
})

const deleteCustomField = createResource({
  url: 'frappe.client.delete',
  makeParams() {
    return {
      doctype: 'FOSS Event Field',
      name: props.row.name,
    }
  },
  onSuccess() {
    props.event.fetch()
    toast.info('Custom field deleted successfully')
    showDialog.value = false
  },
  onError(error) {
    errorMessages.value = error.message
  },
})

const handleCreate = () => {
  const errors = validateFields()
  if (errors.length) {
    errorMessages.value = errors.join(' ')
    return
  }
  errorMessages.value = ''
  createCustomField.fetch()
}

const handleSave = () => {
  const errors = validateFields()
  if (errors.length) {
    errorMessages.value = errors.join(' ')
    return
  }
  errorMessages.value = ''
  updateCustomField.fetch()
}

const handleDelete = () => {
  deleteCustomField.fetch()
}
</script>
