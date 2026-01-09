<template>
  <MailingPage
    doctype="FOSS Chapter"
    :header-component="ChapterHeader"
    document-type="FOSS Chapter"
  />
</template>

<script setup>
import MailingPage from '@/components/mailing/MailingPage.vue'
import ChapterHeader from '@/components/ChapterHeader.vue'

const getCampaignParams = (doc) => {
  return {
    reference_document: doc.name,
    chapter: doc.name,
    document_type: 'FOSS Chapter',
  }
}
</script>
