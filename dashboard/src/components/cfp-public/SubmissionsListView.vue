<script setup>
import Filter from '@/components/ui/Filter.vue'
import { IconSearch } from '@tabler/icons-vue'
import { createResource, FormControl } from 'frappe-ui'
import { ref } from 'vue'
import SubmissionsList from './SubmissionsList.vue'

const props = defineProps({
  eventId: {
    type: String,
    required: true,
  },
})

const submissions = createResource({
  url: 'fossunited.api.proposal.get_event_proposals',
  params: {
    event: props.eventId,
  },
  auto: true,
})

const filterFields = createResource({
  url: 'fossunited.api.proposal.get_public_proposal_filters',
  auto: true,
})

const filters = ref({})
</script>
<template>
  <div class="flex flex-col gap-4 w-full">
    <!-- <div class="w-full flex justify-between items-end gap-4">
      <FormControl v-model="searchTitle" label="Search" variant="outline" icon-left="search">
        <template #suffix>
          <IconSearch class="w-4" />
        </template>
      </FormControl>
      <Filter v-if="filterFields.data" v-model="filters" :docfields="filterFields.data" />
    </div> -->
  </div>
  <Suspense>
    <SubmissionsList v-model="submissions.data" />
  </Suspense>
</template>
