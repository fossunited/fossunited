<template>
  <MailingPage
    doctype="FOSS Chapter Event"
    :header-component="EventHeader"
    document-type="FOSS Chapter Event"
  />
</template>

<script setup>
import MailingPage from '@/components/mailing/MailingPage.vue'
import EventHeader from '@/components/EventHeader.vue'
</script>
