<template>
  <div v-if="localhost.doc">
    <!-- Page Header -->
    <div class="mt-4 flex flex-col justify-between gap-2 md:flex-row">
      <div>
        <div class="text-base-medium">Edit Localhost</div>
        <div class="text-sm text-ink-gray-5">Update venue details and visibility</div>
      </div>

      <div class="flex flex-wrap gap-2">
        <RouterLink :to="{ name: 'ManageLocalhost', params: { id: route.params.id } }">
          <Button variant="subtle" :icon-left="IconArrowLeft" label="Back to Manage" />
        </RouterLink>

        <Button
          :theme="localhost.doc.is_published ? 'red' : 'green'"
          :icon-left="localhost.doc.is_published ? IconCancel : IconUpload"
          :label="localhost.doc.is_published ? 'Unpublish' : 'Publish'"
          :disabled="localhost.setValue.loading"
          @click="togglePublish"
        />
        <Button variant="solid" label="Update Localhost" @click="updateLocalhost" />
      </div>
    </div>

    <!-- Localhost Header -->
    <LocalhostHeader :localhost="localhost.doc" />

    <div class="my-6 rounded-1 border p-4">
      <div class="text-sm-medium mb-3 uppercase">Localhost Overview</div>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <!-- Left: Image -->
        <div>
          <img :src="getImage()" class="aspect-square w-[200px] rounded-6 border object-cover" />

          <div class="mt-3 flex gap-2">
            <FileUploader
              file-types="image/*"
              :private="false"
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

          <div class="mt-2 text-sm text-ink-gray-5">Recommended size: 1:1 square image</div>
        </div>

        <!-- Right: Meta -->
        <div class="flex flex-col gap-4">
          <!-- Accepting Attendees -->
          <div class="md:col-span-2">
            <div class="flex items-center justify-between rounded-5 border p-3">
              <div class="flex flex-col">
                <span class="font-medium text-ink-gray-8"> Accepting Attendees </span>
                <span class="text-sm text-ink-gray-5">
                  Allow attendees to register for this localhost.
                </span>
              </div>
              <Switch v-model="localhost.doc.is_accepting_attendees" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <label class="text-sm-medium text-ink-gray-6">State</label>
              <div class="rounded-5 border bg-surface-gray-1 px-3 py-2">
                {{ localhost.doc.state || '—' }}
              </div>
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-sm-medium text-ink-gray-6">City</label>
              <div class="rounded-5 border bg-surface-gray-1 px-3 py-2">
                {{ localhost.doc.city || '—' }}
              </div>
            </div>
          </div>

          <div>
            <label class="text-sm-medium mb-1 block text-ink-gray-6"> Public Route </label>
            <CopyToClipboardComponent :route="wholeRoute" />
          </div>
        </div>
      </div>
    </div>

    <!-- Details -->
    <div class="my-6 rounded-1 border p-4">
      <div class="text-sm-medium mb-3 uppercase">Localhost Details</div>

      <div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        <FormControl
          v-model="localhost.doc.localhost_name"
          type="text"
          label="Localhost Name"
          size="md"
        />

        <FormControl v-model="localhost.doc.email" type="email" label="Contact Email" size="md" />

        <FormControl
          v-model="localhost.doc.location"
          type="text"
          label="Location Address"
          size="md"
        />

        <FormControl v-model="localhost.doc.map_link" type="url" label="Map Link" size="md" />
      </div>
    </div>
    <!-- Description -->
    <div class="my-6 rounded-1 border p-4">
      <TextEditor
        label="Localhost Description"
        :model-value="localhost.doc.description"
        placeholder="Write about this Localhost… schedule, venue details, what to expect…"
        @update:model-value="($event) => (localhost.doc.description = $event)"
      />
    </div>

    <ManageSponsorView />

    <FormActionBar
      :document-resource="localhost"
      :is-saving="localhost.save.loading"
      @save="updateLocalhost"
    />
  </div>
</template>

<script setup>
import { IconArrowLeft, IconCancel, IconUpload } from '@tabler/icons-vue'
import { createDocumentResource, FileUploader, FormControl, Button, Switch } from 'frappe-ui'
import { computed, provide } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

import CopyToClipboardComponent from '@/components/CopyToClipboardComponent.vue'
import FormActionBar from '@/components/FormActionBar.vue'
import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { toggleDocField } from '@/helpers/utils'
import ManageSponsorView from '@/layout/event/ManageSponsorView.vue'

const route = useRoute()
const router = useRouter()

const localhost = createDocumentResource({
  doctype: 'FOSS Hackathon LocalHost',
  name: route.params.id,
  fields: ['*'],
  auto: true,
  onError(error) {
    toast.error('Failed to load localhost', { description: error.message })
    setTimeout(() => {
      router.push({ name: 'MyLocalhosts' })
    }, 2000)
  },
})
const wholeRoute = computed(() => {
  if (!localhost.doc?.route) return ''
  return `${window.location.origin}/${localhost.doc.route}`
})

provide('event', localhost)

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
  toggleDocField(
    localhost,
    'is_published',
    newValue,
    newValue ? 'Localhost published' : 'Localhost unpublished',
    'Failed to update publish status',
  )
}

const updateLocalhost = () => {
  localhost.save
    .submit()
    .then(() => toast.success('Localhost updated successfully'))
    .catch((err) => toast.error('Failed to update localhost', { description: err.message }))
}
</script>
