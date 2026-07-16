<template>
  <div>
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
        <div class="flex gap-2">
          <Button
            variant="solid"
            label="Create Free Coupon"
            icon-left="plus"
            @click="handleCreate"
          />
          <Button
            variant="outline"
            label="Speaker Coupons"
            icon-left="users"
            :disabled="!canCreateSpeakerCoupons"
            :title="canCreateSpeakerCoupons
              ? 'Auto-create free ticket coupons for approved CFP speakers who don\'t have one yet'
              : 'Only available while event is Live and before the event starts'"
            @click="showSpeakerDialog = true"
          />
        </div>
      </div>

      <SearchListView
        v-if="freeCodes.data && freeCodes.data.length > 0"
        :rows="groupedRows"
        class="mt-4 min-h-[300px]"
        :columns="[
          { label: 'Full Name', key: 'full_name', icon: 'user' },
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
          { label: 'Organization', key: 'company', icon: 'briefcase' },
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
          onRowClick: (row) => handleEdit(row),
        }"
      >
        <template #cell="{ item, row, column }">
          <div v-if="column.key === 'usage'">
            <span
              class="px-2 py-1 rounded text-sm font-medium"
              :class="
                row.used_count >= row.max_count
                  ? 'bg-surface-red-2 text-ink-red-3'
                  : 'bg-surface-green-2 text-ink-green-3'
              "
            >
              {{ row.used_count }} / {{ row.max_count }}
            </span>
          </div>
          <div v-else>
            <span class="text-base truncate text-wrap">{{ item }}</span>
          </div>
        </template>
      </SearchListView>
    </div>
    <Dialog v-model="showSpeakerDialog" :options="{ title: 'Speaker Coupons' }">
      <template #body-content>
        <div class="flex flex-col gap-4">
          <p v-if="speakerPreview.loading" class="text-sm text-ink-gray-5">Loading…</p>
          <div v-else-if="speakerPreview.data" class="text-sm text-ink-gray-7">
            <span class="font-medium">{{ speakerPreview.data.total }}</span> speaker(s) from all approved proposals ·
            <span class="font-medium">{{ speakerPreview.data.already_has }}</span> already have
            coupons ·
            <span class="font-medium text-ink-green-3">{{ speakerPreview.data.will_create }}</span>
            will be created
          </div>
          <FormControl
            v-model="speakerMaxCount"
            label="Tickets per speaker"
            type="number"
            :min="1"
            :max="3"
            description="How many times each coupon can be used (1–3)"
          />
          <p v-if="speakerPreviewErr" class="text-sm text-ink-red-3">{{ speakerPreviewErr }}</p>
        </div>
      </template>
      <template #actions>
        <Button label="Cancel" @click="showSpeakerDialog = false" />
        <Button
          variant="solid"
          label="Create Coupons"
          :loading="bulkCreate.loading"
          :disabled="!speakerPreview.data || speakerPreview.data.will_create === 0 || bulkCreate.loading"
          @click="() => { speakerPreviewErr = ''; bulkCreate.fetch() }"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { defineProps, ref, watchEffect, watch, computed } from 'vue'
import { createResource, Button, Dialog, FormControl } from 'frappe-ui'
import { toast } from 'vue-sonner'
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

// Allow Speaker Coupons only while the event is live and hasn't started yet
const canCreateSpeakerCoupons = computed(() => {
  const { status, event_start_date } = props.event
  if (!status || !event_start_date) return false
  return status === 'Live' && new Date() < new Date(event_start_date)
})
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

const showSpeakerDialog = ref(false)
const speakerMaxCount = ref(1)
const speakerPreviewErr = ref('')

const speakerPreview = createResource({
  url: 'fossunited.api.tickets.get_speaker_coupon_preview',
  makeParams: () => ({ event: props.event.name || route.params.id }),
})

const bulkCreate = createResource({
  url: 'fossunited.api.tickets.bulk_create_speaker_coupons',
  makeParams: () => ({
    event: props.event.name || route.params.id,
    max_count: speakerMaxCount.value,
  }),
  onSuccess(r) {
    toast.success(`Created ${r.created} coupon(s), skipped ${r.skipped}`)
    showSpeakerDialog.value = false
    speakerMaxCount.value = 1
    freeCodes.fetch()
  },
  onError(e) {
    speakerPreviewErr.value = e.message
  },
})

watch(showSpeakerDialog, (open) => {
  if (open) {
    speakerPreviewErr.value = ''
    speakerPreview.fetch()
  }
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
