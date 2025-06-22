<template>
  <Dialog
    v-model="show"
    :options="{
      title: isNew ? 'Add Project Showcase' : 'Manage Project Showcases',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3">
        <FormControl v-model="showcase.showcase_name" label="Showcase Name" required />
        <FormControl v-model="showcase.link" label="Website Link" type="url" required>
          <template #prefix>
            <IconLink class="w-4" />
          </template>
        </FormControl>
        <FormControl v-model="showcase.description" label="Showcase Description" :type="'textarea'" />
        <FileUploaderArea v-model="showcase.image" label="Community Logo" />
        <ErrorMessage :message="errorMessages" class="text-sm -mb-4" />
      </div>
    </template>
    <template #actions>
      <div class="grid grid-flow-col w-full">
        <Button v-if="isNew" label="Add" variant="solid" @click="addShowcase" />
        <Button v-else label="Update" variant="solid" @click="handleShowcaseUpdate" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { toast } from 'vue-sonner'
import { inject, ref } from 'vue'
import { Dialog, FormControl, ErrorMessage, createResource } from 'frappe-ui'
import { IconLink } from '@tabler/icons-vue'
import FileUploaderArea from '@/components/ui/FileUploaderArea.vue'

const event = inject('event')
const errorMessages = ref('')

const show = defineModel('show', { required: true, type: Boolean, default: false })
const showcase = defineModel('showcase', { required: true, type: Object })
const props = defineProps({
  isNew: {
    default: false,
    type: Boolean,
  },
})
const emit = defineEmits(['reload:event'])

const validateFields = () => {
  const errors = []

  if (!showcase.value.showcase_name) {
    errors.push('Showcase name is required')
  }

  if (!showcase.value.link) {
    errors.push('Showcase link is required')
  }

  if (!showcase.value.image) {
    errors.push('Showcase logo is required')
  }

  return errors
}
const addShowcase = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  event.setValue
    .submit({
      project_showcase: [...event.doc.project_showcase, showcase.value],
    })
    .then(() => {
      show.value = false
      showcase.value = {}
      toast.success('Project Showcase Added Successfully!')
    })
    .catch((err) => {
      toast.error(err)
      errorMessages.value = err
    })
}

const handleShowcaseUpdate = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  const fields = {
    showcase_name: showcase.value.showcase_name,
    link: showcase.value.link,
    image: showcase.value.image,
    description: showcase.value.description,
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'Event Project Showcase',
        name: showcase.value.name,
        fieldname: fields,
      }
    },
    onSuccess() {
      toast.success('Project Showcase Updated Successfully!')
      emit('reload:event')
      show.value = false
    },
    onError(err) {
      errorMessages.value = err
      toast.error(err)
    },
    auto: true,
  })
}
</script>
