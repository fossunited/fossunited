<template>
  <div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <ChapterHeader :chapter="chapter" />
    <div class="prose my-4">
      <p class="text-base text-gray-600">Send mass emails to participants and speakers.</p>
    </div>
    <hr />
    <div class="flex flex-col gap-2 mt-2">
      <div class="prose">
        <h3>Campaigns</h3>
      </div>
      <Button
        icon-left="plus"
        label="Create Campaign"
        size="md"
        class="w-fit"
        @click="showCreateDrawer = true"
      />
    </div>
    <CreateCampaignDrawer
      v-model="showCreateDrawer"
      :event="chapter.doc.name"
      :chapter="chapter.doc.name"
      document_type="FOSS Chapter"
      @create-campaign="campaigns.fetch()"
    />
    <ManageCampaignDrawer
      v-model="showManageDrawer"
      :event="chapter.doc.name"
      :chapter="chapter.doc.name"
      :campaign-id="selectedCampaign"
      document_type="FOSS Chapter"
      @update-campaigns="campaigns.fetch()"
    />
    <div v-if="campaigns.loading">
      <LoadingText />
    </div>
    <div v-if="campaigns.data">
      <CampaignList :campaigns="campaigns.data" @row-click="handleRowClick($event)" />
    </div>
  </div>
</template>
<script setup>
import { createDocumentResource, createResource, LoadingText } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, reactive, watch } from 'vue'
import ChapterHeader from '@/components/ChapterHeader.vue'
import CreateCampaignDrawer from '@/components/mailing/CreateCampaignDrawer.vue'
import CampaignList from '@/components/mailing/CampaignList.vue'
import ManageCampaignDrawer from '@/components/mailing/ManageCampaignDrawer.vue'

const route = useRoute()
const showCreateDrawer = ref(false)
const selectedCampaign = ref('')
const showManageDrawer = ref(false)

const campaigns = reactive(
  createResource({
    url: 'fossunited.api.emailing.get_newsletter_campaigns',
    makeParams() {
      return {
        reference_document: chapter.doc.name,
        chapter: chapter.doc.name,
        document_type: 'FOSS Chapter',
      }
    },
  }),
)

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

watch(
  () => chapter.doc,
  (doc) => {
    if (doc) {
      campaigns.fetch()
    }
  },
  {
    deep: true,
    immediate: true,
  },
)

const handleRowClick = (row) => {
  selectedCampaign.value = row
  showManageDrawer.value = true
}

watch(
  () => showManageDrawer.value,
  (val) => {
    if (!val) {
      selectedCampaign.value = ''
    }
  },
)
</script>
