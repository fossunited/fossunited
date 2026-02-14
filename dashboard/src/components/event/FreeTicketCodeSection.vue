<template>
  <FreeTicketCodeDialog
    v-model="showDialog"
    :event="event"
    :in-create-mode="inCreateMode"
    :row="selectedRow"
    @refresh="freeCodes.fetch()"
  />
  <div>
    <div class="prose w-full mb-4">
      <h2 class="mb-1">Free Ticket Codes</h2>
      <p class="text-sm">Manage free ticket codes for this event.</p>
      <Button variant="solid" label="Create Free Coupon" icon-left="plus" @click="handleCreate" />
    </div>

    <SearchListView
      v-if="freeCodes.data && freeCodes.data.length > 0"
      :rows="groupedRows"
      class="mt-4 min-h-[300px]"
      :columns="[
        { label: 'Full Name', key: 'full_name', icon: 'user', width: '200px' },
        { label: 'Coupon ID', key: 'name', width: '100px' },
        { label: 'Email', key: 'mapped_email', icon: 'at-sign' },
        {
          label: 'Used / Max',
          key: 'usage',
          icon: 'check-circle',
          width: '100px',
          exportValue: (row) => `${row.used_count ?? 0} / ${row.max_count ?? 0}`,
        },
        { label: 'Tier', key: 'tier', icon: 'award', width: '200px' },
        { label: 'Organization', key: 'company', icon: 'briefcase', width: '200px' },
      ]"
      row-key="name"
      search-placeholder="Search free coupons…"
      item-label="free coupons"
      export-filename="event_coupons"
      :options="{
        emptyState: {
          title: 'No Free Codes',
          description: 'No free ticket codes have been added yet.',
        },
        selectable: false,
        showTooltip: true,
        resizeColumn: true,
        onRowClick: (row) => handleEdit(row),
      }"
    >
      <template #cell="{ item, row, column }">
        <div v-if="column.key === 'usage'">
          <span
            class="px-2 py-1 rounded text-sm font-medium"
            :class="
              row.used_count >= row.max_count
                ? 'bg-red-100 text-red-700'
                : 'bg-green-100 text-green-700'
            "
          >
            {{ row.used_count }} / {{ row.max_count }}
          </span>
        </div>
        <div v-else>
          <span class="text-base">{{ item }}</span>
        </div>
      </template>
    </SearchListView>
  </div>
</template>

<script setup>
import { defineProps, ref, watchEffect } from 'vue'
import { createResource, Button } from 'frappe-ui'
import FreeTicketCodeDialog from '@/components/event/FreeTicketCodeDialog.vue'
import { useRoute } from 'vue-router'
import SearchListView from '@/components/ui/SearchListView.vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const route = useRoute()
const showDialog = ref(false)
const inCreateMode = ref(false)
const selectedRow = ref({})
const groupedRows = ref([])

const freeCodes = createResource({
  url: 'fossunited.api.tickets.get_event_free_codes',
  makeParams() {
    return {
      event: props.event.name || route.params.id,
    }
  },
  auto: true,
})

watchEffect(() => {
  const rows = Array.isArray(freeCodes.data) ? freeCodes.data : []

  // Group by tier
  const groups = {}

  rows.forEach((code) => {
    const tier = code.tier || 'Other'
    if (!groups[tier]) {
      groups[tier] = []
    }

    // Transform row data with bg_color for usage
    groups[tier].push({
      ...code,
      usage: {
        label: `${code.used_count || 0} / ${code.max_count || 0}`,
        color: code.used_count >= code.max_count ? 'red' : 'green',
        // ^ does not apply in grouping view? so using v-if span method
      },
    })
  })

  // Convert to array format for ListView
  groupedRows.value = Object.entries(groups).map(([tier, tierRows]) => ({
    group: tier,
    collapsed: false,
    rows: tierRows,
  }))
})

const handleEdit = (row) => {
  inCreateMode.value = false
  selectedRow.value = row
  showDialog.value = true
}

const handleCreate = () => {
  selectedRow.value = {}
  inCreateMode.value = true
  showDialog.value = true
}
</script>
