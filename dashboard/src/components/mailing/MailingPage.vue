<template>
  <div v-if="document.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <component :is="headerComponent" v-bind="headerProps" />
    <div class="prose my-4">
      <p class="text-base text-gray-600">{{ infoText }}</p>
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
      v-bind="campaignProps"
      @create-campaign="campaigns.fetch()"
    />
    <ManageCampaignDrawer
      v-model="showManageDrawer"
      v-bind="campaignProps"
      :campaign-id="selectedCampaign"
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
import { ref, reactive, watch, computed } from 'vue'
import CreateCampaignDrawer from '@/components/mailing/CreateCampaignDrawer.vue'
import CampaignList from '@/components/mailing/CampaignList.vue'
import ManageCampaignDrawer from '@/components/mailing/ManageCampaignDrawer.vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  headerComponent: {
    type: [Object, String],
    required: true,
  },
  documentType: {
    type: String,
    default: null,
  },
  getCampaignParams: {
    type: Function,
    default: null,
  },
  infoText: {
    type: String,
    default: 'Send mass emails to participants and speakers.',
  },
})

const route = useRoute()
const showCreateDrawer = ref(false)
const selectedCampaign = ref('')
const showManageDrawer = ref(false)

const campaignParams = computed(() => {
  if (props.getCampaignParams && document.doc) {
    return props.getCampaignParams(document.doc)
  }

  const chapter =
    document.doc.doctype === 'FOSS Chapter'
      ? document.doc.name
      : document.doc.chapter || document.doc.name

  return {
    document_type: document.doc.doctype,
    reference_document: document.doc.name,
    chapter,
  }
})

const document = createDocumentResource({
  doctype: props.doctype,
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const campaigns = reactive(
  createResource({
    url: 'fossunited.api.emailing.get_newsletter_campaigns',
    makeParams() {
      return campaignParams.value
    },
  }),
)

watch(
  () => document.doc,
  (doc) => {
    if (doc) {
      campaigns.fetch()
    }
  },
  {
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

// Computed props for header component
const headerProps = computed(() => {
  const propsMap = {
    'FOSS Chapter': { chapter: document },
    'FOSS Chapter Event': { event: document.doc },
    'FOSS Hackathon LocalHost': { localhost: document.doc },
  }

  return propsMap[props.doctype] || { doc: document.doc }
})

const campaignProps = computed(() => {
  const ctx = campaignParams.value
  if (!ctx.reference_document) return {}

  return {
    event: ctx.reference_document,
    chapter: ctx.chapter,
    document_type: ctx.document_type,
  }
})
</script>
