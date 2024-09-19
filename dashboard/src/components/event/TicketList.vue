<template>
  <div class="prose">
    <h3 class="mb-1">Attendee List</h3>
    <p class="text-sm">List of attendees for this event.</p>
  </div>
  <div class="flex flex-col flex-wrap md:flex-row gap-5 my-2 md:items-end">
    <FormControl
      type="search"
      label="Search"
      placeholder="Search by Name"
      class="md:w-1/4"
      v-model="filters.search_text"
      @input="attendeesList.fetch()"
    />
    <FormControl
      type="select"
      label="Tier"
      class="md:w-1/6"
      v-if="tiers.data"
      :options="tierOptions"
      v-model="filters.tier"
      @change="attendeesList.fetch()"
    />
  </div>
  <ListView
    v-if="attendeesList.data"
    class="h-[540px]"
    :columns="[
      {
        label: 'Name',
        key: 'full_name',
      },
      {
        label: 'Designation',
        key: 'designation',
      },
      {
        label: 'Organization',
        key: 'organization',
      },
      {
        label: 'Tier',
        key: 'tier',
      },
      {
        label: 'T-shirt Addon',
        key: 'wants_tshirt',
        width: 1 / 4,
      },
      {
        label: 'Tshirt Size',
        key: 'tshirt_size',
        width: 1 / 4,
      },
    ]"
    :rows="attendeesList.data"
    :options="{
      selectable: false,
      showTooltip: false,
      resizeColumn: false,
      emptyState: {
        title: 'No attendees for this event',
        description: 'Attendees will be listed here once they buy tickets.',
      },
    }"
  >
    <template #cell="{ item, row, column }" class="even:bg-gray-50">
      <div v-if="column.key === 'wants_tshirt'">
        <Checkbox :model-value="item" :disabled="true" />
      </div>
      <div v-else-if="column.key === 'tshirt_size'">
        <div v-if="!row['wants_tshirt']">
          <div class="text-base">-</div>
        </div>
        <div v-else class="text-base">{{ item }}</div>
      </div>
      <div v-else class="text-base">{{ item }}</div>
    </template>
  </ListView>
  <div v-if="attendeesList.loading" class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>
<script setup>
import { createResource, ListView, LoadingIndicator, Checkbox, FormControl } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { defineProps, reactive, ref, inject } from 'vue'

const session = inject('$session')

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const filters = reactive({
  search_text: '',
  wants_tshirt: false,
})

const tierOptions = ref([])

const tiers = createResource({
  url: 'fossunited.api.tickets.get_ticket_tiers',
  makeParams() {
    return {
      event_id: props.event.data.name,
    }
  },
  auto: true,
  onSuccess(data) {
    let options = []
    options.push({
      label: 'All',
      value: data.map((tier) => tier.title),
    })

    data.forEach((tier) => {
      options.push({
        label: tier.title,
        value: tier.title,
      })
    })
    tierOptions.value = options
    filters.tier = options[0].value
  },
})

const attendeesList = createResource({
  url: 'fossunited.api.tickets.get_sold_tickets',
  makeParams() {
    return {
      event_id: props.event.data.name,
      filters: {
        full_name: ['like', `%${filters.search_text}%`],
        tier: ['in', filters.tier],
      },
      user: session.user,
    }
  },
  loading: true,
  debounce: 500,
  auto: true,
  onError(error) {
    toast.error(error.message)
  },
})
</script>
