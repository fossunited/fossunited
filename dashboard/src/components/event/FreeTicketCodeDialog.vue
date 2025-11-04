<template>
  <Dialog
    v-model="showDialog"
    :options="{
      title: inCreateMode ? 'Create Free Code' : 'Edit Free Code',
      width: 'md',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl
          v-if="!inCreateMode"
          v-model="code.name"
          label="Coupon ID"
          type="text"
          readonly
        />
        <FormControl v-model="code.full_name" label="Full Name" />
        <FormControl v-model="code.mapped_email" label="Email &ast;" type="email" />
        <FormControl
          v-model="code.tier"
          label="Tier &ast;"
          type="select"
          :options="[
            { label: 'Volunteer', value: 'Volunteer' },
            { label: 'Speaker/Workshop Host', value: 'Speaker/Workshop Host' },
            { label: 'Community Partner', value: 'Community Partner' },
            { label: 'Sponsor', value: 'Sponsor' },
            { label: 'Diversity Scholar', value: 'Diversity Scholar' },
            { label: 'Booth Manager', value: 'Booth Manager' },
            { label: 'Other', value: 'Other' },
          ]"
        />
        <FormControl v-model="code.company" label="Organization" />
        <FormControl v-if="code.tier === 'Other'" v-model="code.other_tier" label="Other Tier" />
        <FormControl v-model="code.max_count" label="Max Count &ast;" type="number" :max="30" />
      </div>
      <ErrorMessage :message="errorMessages" />
    </template>
    <template #actions>
      <div class="grid grid-cols-3 gap-2 items-center">
        <Button
          v-if="!inCreateMode"
          class="w-full"
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
import { Dialog, FormControl, ErrorMessage, Button, createResource } from 'frappe-ui'
import { toast } from 'vue-sonner'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  inCreateMode: {
    type: Boolean,
    default: false,
  },
  row: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['refresh'])

const showDialog = defineModel({
  type: Boolean,
  default: false,
})

const code = reactive({
  name: '',
  full_name: '',
  mapped_email: '',
  tier: '',
  company: '',
  other_tier: '',
  max_count: 1,
})

watch(
  () => props.row,
  (row) => {
    code.name = row.name || ''
    code.full_name = row.full_name || ''
    code.mapped_email = row.mapped_email || ''
    code.tier = row.tier || ''
    code.company = row.company || ''
    code.other_tier = row.other_tier || ''
    code.max_count = row.max_count || 1
  },
  { immediate: true },
)

const errorMessages = ref('')

const validateFields = () => {
  const errors = []
  if (!code.mapped_email) errors.push('Email is required.')
  if (!code.tier) errors.push('Tier is required.')
  if (!code.max_count || code.max_count < 1) errors.push('Max count must be at least 1.')
  if (code.max_count > 30) errors.push('Max count cannot exceed 30.')
  return errors
}

const createCode = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'Event Free Ticket Code',
        event: props.event.data.name,
        full_name: code.full_name,
        mapped_email: code.mapped_email,
        tier: code.tier,
        company: code.company,
        other_tier: code.other_tier,
        max_count: code.max_count,
      },
    }
  },
  onSuccess() {
    toast.success('Free code created successfully')
    showDialog.value = false
    // Trigger refresh of parent list
    window.location.reload()
  },
  onError(error) {
    errorMessages.value = error.message
  },
})

const updateCode = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'Event Free Ticket Code',
      name: props.row.name,
      fieldname: {
        full_name: code.full_name,
        mapped_email: code.mapped_email,
        tier: code.tier,
        company: code.company,
        other_tier: code.other_tier,
        max_count: code.max_count,
      },
    }
  },
  onSuccess() {
    toast.success('Free code updated successfully')
    showDialog.value = false
    window.location.reload()
  },
  onError(error) {
    errorMessages.value = error.message
  },
})

const deleteCode = createResource({
  url: 'frappe.client.delete',
  makeParams() {
    return {
      doctype: 'Event Free Ticket Code',
      name: props.row.name,
    }
  },
  onSuccess() {
    toast.info('Free code deleted successfully')
    showDialog.value = false
    window.location.reload()
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
  createCode.fetch()
}

const handleSave = () => {
  const errors = validateFields()
  if (errors.length) {
    errorMessages.value = errors.join(' ')
    return
  }
  errorMessages.value = ''
  updateCode.fetch()
}

const handleDelete = () => {
  deleteCode.fetch()
}
</script>
