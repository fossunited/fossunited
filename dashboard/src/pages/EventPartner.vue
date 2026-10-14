<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <EventHeader :event="event.doc" />
    <div class="flex flex-col my-6">
      <div class="font-semibold text-ink-gray-8 border-b-2 pb-2">Sponsorship Deck</div>
      <div class="p-2 my-1 flex flex-col sm:flex-row gap-4 sm:items-end max-w-lg">
        <FormControl
          v-model="event.doc.deck_link"
          type="url"
          size="md"
          label="Deck Link"
          description="Link to the event's slide/sponsorship deck. Shared with partners and sponsors."
          class="flex-1"
        />
        <Button label="Save" :loading="event.setValue.loading" @click="saveDeckLink" />
        <FileUploader
          :file-types="'application/pdf'"
          :validate-file="validateDeckFile"
          @success="(file) => setDeckLink(file.file_url)"
          @failure="
            (error) => toast.error('Failed to upload deck', { description: error?.message })
          "
        >
          <template #default="{ progress, uploading, error, openFileSelector }">
            <div class="flex flex-col gap-1">
              <Button
                :variant="'subtle'"
                :label="uploading ? `Uploading ${progress}` : 'Or upload a PDF'"
                @click="openFileSelector"
              />
              <div v-if="error" class="text-sm text-ink-red-4">{{ error }}</div>
            </div>
          </template>
        </FileUploader>
      </div>
    </div>
    <ManageSponsorView />
    <ManagePartnerView />
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { inject } from 'vue'
import { FileUploader, FormControl } from 'frappe-ui'
import { toast } from 'vue-sonner'
import ManageSponsorView from '@/layout/event/ManageSponsorView.vue'
import ManagePartnerView from '@/layout/event/ManagePartnerView.vue'

const event = inject('event')

const saveDeckLink = () => {
  event.setValue
    .submit({ deck_link: event.doc.deck_link })
    .then(() => toast.success('Deck link updated successfully'))
    .catch((error) => toast.error('Failed to update deck link', { description: error.message }))
}

const validateDeckFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (extn !== 'pdf') {
    toast.error('Only PDF files are allowed')
    return 'Only PDF files are allowed'
  }
}

const setDeckLink = (fileUrl) => {
  const absoluteUrl = fileUrl.startsWith('http') ? fileUrl : window.location.origin + fileUrl
  event.doc.deck_link = absoluteUrl
  event.setValue
    .submit({ deck_link: absoluteUrl })
    .then(() => toast.success('Deck uploaded successfully'))
    .catch((error) => toast.error('Failed to save deck link', { description: error.message }))
}
</script>
