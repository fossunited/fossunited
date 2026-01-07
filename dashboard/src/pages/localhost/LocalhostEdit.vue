<template>
  <LocalhostLayout
    :is-validated="isValidated"
    v-model:show-dialog="showDialog"
    :dialog-message="dialogMessage"
  >
    <div v-if="localhost.doc">
      <!-- Page Header -->
      <div class="flex flex-col md:flex-row justify-between gap-2 mt-4">
        <div>
          <div class="text-base font-medium">Edit Localhost</div>
          <div class="text-sm text-gray-600">Update venue details and visibility</div>
        </div>

        <div class="flex flex-wrap gap-2">
          <RouterLink :to="{ name: 'ManageLocalhost', params: { id: route.params.id } }">
            <Button variant="subtle" icon-left="arrow-left" label="Back to Manage" />
          </RouterLink>

          <Button
            :theme="localhost.doc.is_published ? 'red' : 'green'"
            :icon-left="localhost.doc.is_published ? 'slash' : 'upload'"
            :label="localhost.doc.is_published ? 'Unpublish' : 'Publish'"
            @click="togglePublish"
          />
          <Button variant="solid" label="Update Localhost" @click="updateLocalhost" />
        </div>
      </div>

      <!-- Localhost Header -->
      <LocalhostHeader :localhost="localhost.doc" />

      <div class="rounded-sm border p-4 my-6">
        <div class="text-sm uppercase font-medium mb-3">Localhost Overview</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Left: Image -->
          <div>
            <img
              :src="getImage()"
              class="w-[200px] aspect-square object-cover border rounded-lg"
            />

            <div class="flex gap-2 mt-3">
              <FileUploader
                file-types="image/*"
                :validate-file="validateImage"
                @success="setImage"
              >
                <template #default="{ uploading, progress, openFileSelector }">
                  <Button
                    variant="subtle"
                    size="md"
                    :label="uploading ? `Uploading ${progress}%` : 'Upload Image'"
                    @click="openFileSelector"
                  />
                </template>
              </FileUploader>

              <Button
                v-if="localhost.doc.image"
                variant="subtle"
                theme="red"
                label="Remove Image"
                @click="() => setImage({ file_url: '' })"
              />
            </div>

            <div class="text-sm text-gray-600 mt-2">Recommended size: 1:1 square image</div>
          </div>

          <!-- Right: Meta -->
          <div class="flex flex-col gap-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">State</label>
                <div class="px-3 py-2 border rounded-md bg-gray-50">
                  {{ localhost.doc.state || '—' }}
                </div>
              </div>

              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">City</label>
                <div class="px-3 py-2 border rounded-md bg-gray-50">
                  {{ localhost.doc.city || '—' }}
                </div>
              </div>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 mb-1 block"> Public Route </label>
              <CopyToClipboardComponent :route="wholeRoute" />
            </div>
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="rounded-sm border p-4 my-6">
        <div class="text-sm uppercase font-medium mb-3">Localhost Details</div>

        <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-6">
          <FormControl
            v-model="localhost.doc.localhost_name"
            type="text"
            label="Localhost Name"
            size="md"
          />

          <FormControl
            v-model="localhost.doc.email"
            type="email"
            label="Contact Email"
            size="md"
          />

          <FormControl
            v-model="localhost.doc.location"
            type="text"
            label="Location Address"
            size="md"
          />

          <FormControl v-model="localhost.doc.map_link" type="url" label="Map Link" size="md" />

          <!-- Accepting Attendees -->
          <div class="md:col-span-2">
            <div class="flex items-center justify-between p-3 border rounded-md">
              <div class="flex flex-col">
                <span class="font-medium text-gray-800"> Accepting Attendees </span>
                <span class="text-sm text-gray-600">
                  Allow attendees to register for this localhost.
                </span>
              </div>
              <Switch v-model="localhost.doc.is_accepting_attendees" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </LocalhostLayout>
</template>

<script setup>
import { createDocumentResource, FileUploader, FormControl, Button, Switch } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'
import LocalhostLayout from '@/components/localhost/LocalhostLayout.vue'
import CopyToClipboardComponent from '@/components/CopyToClipboardComponent.vue'
import { LocalhostValidation } from '@/components/localhost/LocalhostValidation'

const route = useRoute()
const router = useRouter()
const wholeRoute = ref('')

const { isValidated, dialogMessage, showDialog, validateSessionUser } = LocalhostValidation(
  route.params.id,
  'MyLocalhosts',
)

const localhost = createDocumentResource({
  doctype: 'FOSS Hackathon LocalHost',
  name: route.params.id,
  fields: ['*'],
  auto: false,
  onSuccess(doc) {
    wholeRoute.value = `${window.location.origin}/${doc.route}`
  },
  onError(error) {
    toast.error('Failed to load localhost', { description: error.message })
    setTimeout(() => {
      router.push({ name: 'MyLocalhosts' })
    }, 2000)
  },
})

const validateImage = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
    return 'Only PNG, Webp & JPG images are allowed'
  }
}

const getImage = () => {
  return localhost.doc.image || '/assets/fossunited/images/localhost_placeholder.svg'
}

const setImage = (file) => {
  localhost.setValue.submit({ image: file.file_url })
  toast.success(file.file_url ? 'Image updated' : 'Image removed')
}

const togglePublish = () => {
  const newValue = !localhost.doc.is_published
  localhost.setValue.submit({ is_published: newValue })
  toast[newValue ? 'success' : 'warning'](
    newValue ? 'Localhost published' : 'Localhost unpublished',
  )
}

const updateLocalhost = () => {
  localhost.save
    .submit()
    .then(() => toast.success('Localhost updated successfully'))
    .catch((err) => toast.error('Failed to update localhost', { description: err.message }))
}

onMounted(() => {
  validateSessionUser(() => {
    localhost.reload()
  })
})
</script>
