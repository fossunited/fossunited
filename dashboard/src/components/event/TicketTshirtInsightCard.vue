<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'T-shirt Allocation & Logistics Breakdown',
      size: '3xl',
    }"
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
  >
    <template #body-content>
      <div class="flex flex-col gap-4 text-sm">
        <p class="text-ink-gray-6">
          Real-time breakdown of T-shirt allocations, handouts, and remaining pending stock across
          ticket categories.
        </p>

        <!-- Top Overview Stats -->
        <div class="grid grid-cols-3 gap-3 p-3 bg-surface-gray-1 rounded-md text-center">
          <div class="flex flex-col">
            <span class="text-xs text-ink-gray-5 uppercase font-medium">Total Allocated</span>
            <span class="text-xl font-bold text-ink-gray-9">{{ totalStats.allocated }}</span>
          </div>
          <div class="flex flex-col">
            <span class="text-xs text-ink-gray-5 uppercase font-medium">Delivered / Handed Out</span>
            <span class="text-xl font-bold text-ink-green-3">{{ totalStats.delivered }}</span>
          </div>
          <div class="flex flex-col">
            <span class="text-xs text-ink-gray-5 uppercase font-medium">Pending Collection</span>
            <span class="text-xl font-bold text-ink-amber-3">{{ totalStats.pending }}</span>
          </div>
        </div>

        <!-- Category Tabs -->
        <div class="flex border-b border-outline-gray-2 gap-2 text-sm font-medium">
          <button
            type="button"
            v-for="tab in TABS"
            :key="tab.key"
            :aria-pressed="activeTab === tab.key"
            class="px-3 py-2 border-b-2 transition-colors"
            :class="
              activeTab === tab.key
                ? 'border-ink-gray-9 text-ink-gray-9 font-semibold'
                : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'
            "
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content: Size Matrix Table -->
        <div v-if="activeTab !== 'tier'" class="overflow-x-auto">
          <table class="w-full text-left border-collapse" role="table">
            <thead>
              <tr class="bg-surface-gray-2 text-xs uppercase text-ink-gray-6">
                <th class="p-2.5 border-b font-semibold">Size</th>
                <th class="p-2.5 border-b font-semibold text-center">Allocated</th>
                <th class="p-2.5 border-b font-semibold text-center">Delivered</th>
                <th class="p-2.5 border-b font-semibold text-center">Pending</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr
                v-for="row in currentCategoryRows"
                :key="row.size"
                :class="row.size === 'Unspecified' && row.allocated > 0 ? 'bg-surface-amber-1' : ''"
              >
                <td class="p-2.5 font-medium flex items-center gap-1.5">
                  <span
                    v-if="row.size === 'Unspecified'"
                    class="px-1.5 py-0.5 text-xs rounded bg-surface-amber-2 text-ink-amber-3 font-semibold"
                  >
                    Missing Size
                  </span>
                  <span v-else class="font-mono text-base font-bold">{{ row.size }}</span>
                </td>
                <td class="p-2.5 text-center font-medium">{{ row.allocated }}</td>
                <td class="p-2.5 text-center text-ink-green-3 font-medium">{{ row.delivered }}</td>
                <td class="p-2.5 text-center font-bold" :class="row.pending > 0 ? 'text-ink-amber-3' : 'text-ink-gray-4'">
                  {{ row.pending }}
                </td>
              </tr>
              <tr class="bg-surface-gray-1 font-bold text-ink-gray-9">
                <td class="p-2.5">Total</td>
                <td class="p-2.5 text-center">{{ currentCategoryTotal.allocated }}</td>
                <td class="p-2.5 text-center text-ink-green-3">{{ currentCategoryTotal.delivered }}</td>
                <td class="p-2.5 text-center text-ink-amber-3">{{ currentCategoryTotal.pending }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tab Content: By Tier -->
        <div v-else class="overflow-x-auto space-y-4">
          <table class="w-full text-left border-collapse" role="table">
            <thead>
              <tr class="bg-surface-gray-2 text-xs uppercase text-ink-gray-6">
                <th class="p-2.5 border-b font-semibold">Tier</th>
                <th class="p-2.5 border-b font-semibold text-center">Allocated</th>
                <th class="p-2.5 border-b font-semibold text-center">Delivered</th>
                <th class="p-2.5 border-b font-semibold text-center">Pending</th>
                <th class="p-2.5 border-b font-semibold">Size Distribution</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr v-for="tier in insight.tier_breakdown || []" :key="tier.title">
                <td class="p-2.5 font-medium">{{ tier.title }}</td>
                <td class="p-2.5 text-center">{{ tier.allocated }}</td>
                <td class="p-2.5 text-center text-ink-green-3">{{ tier.delivered }}</td>
                <td class="p-2.5 text-center font-bold text-ink-amber-3">{{ tier.pending }}</td>
                <td class="p-2.5 text-xs text-ink-gray-6">
                  <span
                    v-for="(count, sz) in tier.sizes"
                    :key="sz"
                    class="inline-block mr-2 px-1.5 py-0.5 rounded bg-surface-gray-2 font-mono"
                  >
                    {{ sz }}: {{ count }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Logistics Advisory Note -->
        <div class="p-3 bg-surface-gray-1 rounded text-xs text-ink-gray-6 leading-relaxed">
          💡 <strong>Logistics Tip:</strong> Pre-paid sizes are guaranteed for buyers. Do not swap or
          reassign common sizes (M & L) at the registration desk without verifying buffer counts.
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Summary Card on Dashboard -->
  <div class="flex flex-col w-full border rounded-sm p-4 bg-surface-white">
    <div class="text-sm flex gap-2 items-center uppercase font-semibold text-ink-gray-7">
      <IconShirtFilled class="w-5 h-5 text-ink-gray-9" aria-hidden="true" />
      <span>T-shirts Logistics</span>
    </div>
    <div class="flex flex-col gap-3 mt-4">
      <div class="flex items-baseline justify-between">
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold text-ink-gray-9">{{ totalStats.allocated }}</span>
          <span class="text-xs text-ink-gray-5 uppercase font-medium">Allocated</span>
        </div>
        <Button class="w-fit" label="View Breakdown" size="sm" @click="showDialog = true" />
      </div>
      <div class="flex gap-2 flex-wrap text-xs font-medium">
        <span class="px-2 py-0.5 rounded bg-surface-green-2 text-ink-green-3">
          ✓ {{ totalStats.delivered }} Delivered
        </span>
        <span class="px-2 py-0.5 rounded bg-surface-amber-2 text-ink-amber-3">
          ⏳ {{ totalStats.pending }} Pending
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Dialog, Button } from 'frappe-ui'
import { computed, defineProps, ref } from 'vue'
import { IconShirtFilled } from '@tabler/icons-vue'

const showDialog = ref(false)
const activeTab = ref('all')

const props = defineProps({
  insight: {
    type: Object,
    required: true,
  },
})

const TABS = [
  { key: 'all', label: 'All T-shirts' },
  { key: 'prepaid', label: 'Pre-Paid' },
  { key: 'free_coupon', label: 'Free Passes & Coupons' },
  { key: 'tier', label: 'By Tier' },
]

const SIZE_ORDER = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', 'Unspecified']

const totalStats = computed(() => ({
  allocated: props.insight.tshirts_sold || props.insight.categories?.total?.allocated || 0,
  delivered: props.insight.tshirts_delivered || props.insight.categories?.total?.delivered || 0,
  pending: props.insight.tshirts_pending || props.insight.categories?.total?.pending || 0,
}))

const currentCategoryData = computed(() => {
  const cats = props.insight.categories || {}
  if (activeTab.value === 'prepaid') return cats.prepaid || { sizes: {}, allocated: 0, delivered: 0, pending: 0 }
  if (activeTab.value === 'free_coupon') return cats.free_coupon || { sizes: {}, allocated: 0, delivered: 0, pending: 0 }
  return cats.total || { sizes: {}, allocated: 0, delivered: 0, pending: 0 }
})

const currentCategoryRows = computed(() => {
  const sizeMap = currentCategoryData.value.sizes || {}
  const rows = Object.entries(sizeMap).map(([size, counts]) => ({
    size,
    allocated: typeof counts === 'object' ? counts.allocated : counts,
    delivered: typeof counts === 'object' ? counts.delivered : 0,
    pending: typeof counts === 'object' ? counts.pending : counts,
  }))

  return rows
    .filter((r) => r.allocated > 0 || r.size === 'Unspecified')
    .sort((a, b) => {
      const idxA = SIZE_ORDER.indexOf(a.size) === -1 ? 99 : SIZE_ORDER.indexOf(a.size)
      const idxB = SIZE_ORDER.indexOf(b.size) === -1 ? 99 : SIZE_ORDER.indexOf(b.size)
      return idxA - idxB
    })
})

const currentCategoryTotal = computed(() => {
  const rows = currentCategoryRows.value
  return {
    allocated: rows.reduce((acc, r) => acc + (r.allocated || 0), 0),
    delivered: rows.reduce((acc, r) => acc + (r.delivered || 0), 0),
    pending: rows.reduce((acc, r) => acc + (r.pending || 0), 0),
  }
})
</script>
