<template>
  <MailingPage
    doctype="FOSS Hackathon LocalHost"
    :header-component="LocalhostHeader"
    document-type="FOSS Hackathon LocalHost"
    :get-campaign-params="getCampaignParams"
    info-text="Send mass emails to localhost participants."
  />
</template>

<script setup>
import MailingPage from '@/components/mailing/MailingPage.vue'
import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'
import { createDocumentResource, createResource, LoadingText } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()

const document = createDocumentResource({
  doctype: 'FOSS Hackathon LocalHost',
  name: route.params.id,
  fields: ['parent_hackathon'],
  auto: true,
  onSuccess(doc) {
    hackathon.reload({
      name: doc.parent_hackathon,
    })
  },
})

const hackathonChapter = ref(null)

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon',
  auto: false,
  onSuccess(doc) {
    hackathonChapter.value = doc.chapter
  },
})

const getCampaignParams = (doc) => {
  return {
    reference_document: doc.name,
    chapter: hackathonChapter.value,
    document_type: 'FOSS Hackathon LocalHost',
  }
}
</script>
