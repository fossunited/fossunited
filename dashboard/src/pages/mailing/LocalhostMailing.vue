<template>
  <MailingPage
    :key="campaignKey"
    doctype="FOSS Hackathon LocalHost"
    :header-component="LocalhostHeader"
    :get-campaign-params="getCampaignParams"
    info-text="Send mass emails to localhost participants."
  />
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import MailingPage from '@/components/mailing/MailingPage.vue'
import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'

const route = useRoute()
const hackathonChapter = ref(null)
const campaignKey = ref(0)

const localhost = createDocumentResource({
  doctype: 'FOSS Hackathon LocalHost',
  name: route.params.id,
  fields: ['parent_hackathon'],
  auto: true,
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon',
  auto: false,
})

watch(
  () => route.params.id,
  () => {
    hackathonChapter.value = null
    localhost.reload()
    campaignKey.value++
  },
)

watch(
  () => localhost.doc?.parent_hackathon,
  (parent) => {
    if (parent) {
      hackathon.fetch({ name: parent }).then((data) => {
        hackathonChapter.value = data.chapter
        campaignKey.value++
      })
    } else {
      hackathonChapter.value = null
    }
  },
  { immediate: true },
)

const getCampaignParams = (doc) => ({
  reference_document: doc.name,
  chapter: hackathonChapter.value,
  document_type: 'FOSS Hackathon LocalHost',
})
</script>
