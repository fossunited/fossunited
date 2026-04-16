<template>
  <div class="prose">
    <h3 class="mb-1">Attendee List</h3>
    <p class="text-sm">List of attendees for this event.</p>
  </div>
  <SearchListView
    v-if="attendeesList.data"
    :rows="tickets"
    :columns="columns"
    row-key="id"
    group-by="tier"
    search-placeholder="Search attendees..."
    item-label="attendees"
    export-filename="event_attendees"
    :export-columns="[{ label: 'Tier', key: 'tier' }, ...columns]"
    :options="{
      selectable: false,
      emptyState: {
        title: 'No attendees yet',
        description: 'Attendees will appear once they register.',
      },
    }"
  >
    <template #group-header="{ group }">
      <span class="text-base font-medium"> {{ group.group }} ({{ group.rows.length }}) </span>
    </template>

    <template #cell="{ item, column }">
      <Checkbox v-if="column.key === 'wants_tshirt'" :model-value="item" disabled />
      <div v-else class="text-sm truncate text-wrap">{{ item || '-' }}</div>
    </template>
  </SearchListView>
  <div v-if="attendeesList.loading" class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>

<script setup>
import { createResource, LoadingIndicator, Checkbox } from 'frappe-ui'
import { toast } from 'vue-sonner'
import SearchListView from '@/components/ui/SearchListView.vue'
import { defineProps, computed } from 'vue'

const props = defineProps({
  event: { type: Object, required: true },
})

const attendeesList = createResource({
  url: 'fossunited.api.tickets.get_tickets_with_custom_fields',
  makeParams() {
    return { event_id: props.event.data.name }
  },
  auto: true,
  debounce: 500,
  onError: (e) => toast.error(e.message),
})

const ticket_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Chapter Event',
    name: props.event.data.name,
    fields: ['custom_fields'],
  },
  auto: true,
})

const tickets = computed(() => attendeesList.data || [])

const columns = computed(() => [
  { label: 'Name', key: 'full_name', width: '200px' },
  { label: 'Designation', key: 'designation', width: '200px' },
  { label: 'Organization', key: 'organization', width: '200px' },
  { label: 'T-shirt Addon', key: 'wants_tshirt', width: '100px' },
  { label: 'Tshirt Size', key: 'tshirt_size', width: '100px' },
  ...(ticket_form.data?.custom_fields || []).map((f) => ({
    label: f.label,
    key: f.field_name,
    width: '200px',
  })),
])
</script>
