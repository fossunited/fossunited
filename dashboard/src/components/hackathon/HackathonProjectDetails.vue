<template>
  <div class="flex flex-col md:grid md:grid-cols-2 mb-4 gap-4 md:items-center">
    <div class="flex flex-col py-1">
      <div class="text-xs text-gray-600">Project's Public Page</div>
      <CopyToClipboard :route="getRoute(project.data.route)" />
    </div>
    <FormControl
      label="Short Description"
      v-model="project.data.short_description"
      placeholder="Enter a short description of the project"
    />
    <FormControl
      label="Repository Link"
      v-model="project.data.repo_link"
      :disabled="project.data.is_partner_project"
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
          class="icon w-5 icon-tabler icons-tabler-outline icon-tabler-brand-github"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path
            d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"
          />
        </svg>
      </template>
    </FormControl>
    <FormControl label="Demo Link" v-model="project.data.demo_link" />
    <TextEditor
      class="col-span-2 mt-2"
      label="Project Description"
      :modelValue="project.data.description"
      placeholder="Enter a detailed description of the project"
      @update:modelValue="($event) => (project.data.description = $event)"
    />
  </div>
  <div>
    <ErrorMessage :message="errorMessage" />
    <div class="grid grid-cols-1 md:grid-cols-2 place-items-end">
      <div></div>
      <Button
        @click="handleProjectUpdate"
        variant="solid"
        theme="green"
        label="Save"
        size="md"
        class="w-full md:w-2/3"
      />
    </div>
  </div>
</template>
<script setup>
import CopyToClipboard from '@/components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/TextEditor.vue'
import { defineProps, defineEmits, ref } from 'vue'
import { FormControl, ErrorMessage, createResource } from 'frappe-ui'
import { toast } from 'vue-sonner'

const props = defineProps({
  project: Object,
})

const getRoute = (route) => {
  return `${window.location.origin}/${route}`
}

const errorMessage = ref('')

const updateProjectErrors = () => {
  const errors = []

  if (!props.project.data.short_description) {
    errors.push('Short description cannot be empty')
  }
  if (!props.project.data.description) {
    errors.push('Description cannot be empty')
  }
  if (!props.project.data.repo_link) {
    errors.push('Repository link cannot be empty')
  }
  if (
    props.project.data.repo_link &&
    !props.project.data.repo_link.startsWith('https://')
  ) {
    errors.push('Enter a valid repo link')
  }

  return errors
}

const handleProjectUpdate = () => {
  if (updateProjectErrors().length) {
    errorMessage.value = updateProjectErrors().join(', ')
    return
  } else {
    errorMessage.value = ''
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Hackathon Project',
        name: props.project.data.name,
        fieldname: {
          short_description: props.project.data.short_description,
          description: props.project.data.description,
          repo_link: props.project.data.repo_link,
          demo_link: props.project.data.demo_link,
        },
      }
    },
    auto: true,
    onSuccess(data) {
      toast.success('Project updated successfully')
    },
    onError(error) {
      toast.error('Failed to update project' + error.message)
    },
  })
}
</script>
