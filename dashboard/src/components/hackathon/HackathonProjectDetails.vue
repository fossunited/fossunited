<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="flex flex-col md:grid md:grid-cols-2 mb-4 gap-4 md:items-center">
    <div class="flex flex-col py-1">
      <div class="text-xs text-ink-gray-5">Project's Public Page</div>
      <CopyToClipboard :route="getRoute(projectDoc.doc.route)" />
    </div>
    <FormControl
      v-model="projectDoc.doc.short_description"
      label="Short Description"
      placeholder="Enter a short description of the project"
      :disabled="isHackathonEnded"
    />
    <FormControl
      v-model="projectDoc.doc.repo_link"
      label="Repository Link"
      :disabled="isHackathonEnded || projectDoc.doc.is_partner_project"
    >
      <template #prefix>
        <IconBrandGithub class="w-4" />
      </template>
    </FormControl>
    <FormControl
      v-model="projectDoc.doc.demo_link"
      label="Demo Link"
      :disabled="isHackathonEnded"
    />
    <div class="col-span-2 mt-2" :class="{ 'pointer-events-none opacity-60': isHackathonEnded }">
      <TextEditor
        label="Project Description"
        :model-value="projectDoc.doc.description"
        placeholder="Enter a detailed description of the project"
        @update:model-value="($event) => (projectDoc.doc.description = $event)"
      />
    </div>
  </div>
  <div v-if="!isHackathonEnded">
    <ErrorMessage :message="errorMessage" />
    <div class="flex flex-row-reverse">
      <Button
        variant="solid"
        theme="green"
        label="Save"
        size="md"
        class="w-full md:w-2/5"
        @click="handleProjectUpdate"
      />
    </div>
  </div>
</template>
<script setup>
import CopyToClipboard from '@/components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { defineProps, defineEmits, ref } from 'vue'
import { FormControl, ErrorMessage, createDocumentResource } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { IconBrandGithub } from '@tabler/icons-vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
  isHackathonEnded: {
    type: Boolean,
    default: false,
  },
})

const projectDoc = createDocumentResource({
  doctype: 'FOSS Hackathon Project',
  name: props.project.data.name,
  fields: ['*'],
  auto: true,
})

const getRoute = (route) => {
  return `${window.location.origin}/${route}`
}

const errorMessage = ref('')

const updateProjectErrors = () => {
  const errors = []

  if (!projectDoc.doc.short_description) {
    errors.push('Short description cannot be empty')
  }
  if (!projectDoc.doc.description) {
    errors.push('Description cannot be empty')
  }
  if (!projectDoc.doc.repo_link) {
    errors.push('Repository link cannot be empty')
  }
  if (projectDoc.doc.repo_link && !projectDoc.doc.repo_link.startsWith('https://')) {
    errors.push('Enter a valid repo link starting with https://')
  }
  if (projectDoc.doc.demo_link && !projectDoc.doc.demo_link.startsWith('https://')) {
    errors.push('Enter a valid demo link starting with https://')
  }

  return errors
}

const handleProjectUpdate = () => {
  const errors = updateProjectErrors()
  if (errors.length) {
    errorMessage.value = errors.join(', ')
    return
  }
  errorMessage.value = ''
  projectDoc.save
    .submit()
    .then(() => {
      toast.success('Project updated successfully')
    })
    .catch((err) => {
      showError(err, 'Failed to save project')
    })
}
</script>
