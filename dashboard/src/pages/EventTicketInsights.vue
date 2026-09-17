<template>
  <Dialog
    v-model="showChartDialog"
    :options="{
      title: 'Tickets Purchased Over Time',
      size: '6xl',
    }"
  >
    <template #body-content>
      <div class="flex justify-end gap-2 mb-2">
        <Button label="Download CSV" variant="subtle" @click="downloadChartCsv">
          <template #prefix><IconDownload class="w-4 h-4" /></template>
        </Button>
        <Button label="Download PNG" variant="subtle" @click="downloadChartPng(expandedChart)">
          <template #prefix><IconDownload class="w-4 h-4" /></template>
        </Button>
      </div>
      <div ref="expandedChart" class="h-[65vh] min-h-[420px]">
        <AxisChart :config="ticketsSoldChartConfig" />
      </div>
    </template>
  </Dialog>
  <div v-if="ticket_insights.data" class="flex flex-col gap-6">
    <div class="flex flex-col gap-4">
      <div class="flex items-start justify-between gap-4">
        <div class="prose">
          <h2 class="mb-1">Insights</h2>
          <p class="text-sm">Get insights about the tickets sold for this event.</p>
        </div>
        <Button
          label="Refresh"
          variant="subtle"
          size="sm"
          :loading="ticket_insights.loading || ticket_checkin_insights.loading"
          @click="
            () => {
              ticket_insights.fetch()
              ticket_checkin_insights.fetch()
            }
          "
        >
          <template #prefix>
            <IconRefresh class="w-4 h-4" />
          </template>
        </Button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <TicketTierInsightCard :tier="today_stats" />
        <TicketTshirtInsightCard :insight="ticket_insights.data.tshirt_insights" />
      </div>
      <div
        v-if="ticket_insights.data.tickets_sold_over_time?.length"
        class="w-full max-w-3xl rounded border border-outline-gray-2 bg-surface-white"
      >
        <div class="flex flex-wrap items-center justify-between gap-2 px-4 pt-3">
          <div>
            <h3 class="text-sm font-medium text-ink-gray-9">Tickets Purchased Over Time</h3>
            <p class="text-xs text-ink-gray-5">Cumulative purchases by ticket type</p>
          </div>
          <div class="flex items-center gap-1">
            <Button label="CSV" variant="ghost" size="sm" @click="downloadChartCsv">
              <template #prefix><IconDownload class="w-4 h-4" /></template>
            </Button>
            <Button label="PNG" variant="ghost" size="sm" @click="downloadChartPng(compactChart)">
              <template #prefix><IconDownload class="w-4 h-4" /></template>
            </Button>
            <Button label="Expand" variant="ghost" size="sm" @click="showChartDialog = true">
              <template #prefix><IconArrowsMaximize class="w-4 h-4" /></template>
            </Button>
          </div>
        </div>
        <div ref="compactChart" class="h-[280px]">
          <AxisChart :config="ticketsSoldChartConfig" />
        </div>
      </div>
      <div class="prose mt-4">
        <h4>Tier Insights</h4>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <TicketTierInsightCard
          v-for="tier in ticket_insights.data.tier_data"
          :key="tier.title"
          :tier="tier"
        />
      </div>

      <div
        v-if="ticket_checkin_insights.data?.daily_data?.length"
        class="flex flex-col gap-4 my-2"
      >
        <div class="prose">
          <h4>Daily Check-in Insights</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <TicketTierInsightCard
            v-for="day in ticket_checkin_insights.data.daily_data"
            :key="day.title"
            :tier="day"
          />
        </div>
      </div>

      <div class="flex flex-col gap-4">
        <TicketList :event="event" />
      </div>
    </div>
  </div>
  <div v-else class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>
<script setup>
import { computed, defineProps, reactive, ref } from 'vue'
import { AxisChart, createResource, LoadingIndicator, Button, Dialog } from 'frappe-ui'
import { IconArrowsMaximize, IconDownload, IconRefresh } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import TicketTierInsightCard from '@/components/event/TicketTierInsightCard.vue'
import TicketTshirtInsightCard from '@/components/event/TicketTshirtInsightCard.vue'
import TicketList from '@/components/event/TicketList.vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const today_stats = reactive({
  title: 'Total Tickets Sold',
  total_sold: 0,
  tickets_sold_today: 0,
  tier_capacity: false,
})

const showChartDialog = ref(false)
const compactChart = ref(null)
const expandedChart = ref(null)
const chartColors = ['#5E64FF', '#2F9E44', '#F08C00', '#E64980', '#15AABF', '#7950F2']

const ticket_insights = createResource({
  url: 'fossunited.api.tickets.get_tickets_insights',
  makeParams() {
    return {
      event_id: props.event.data.name,
    }
  },
  loading: true,
  auto: true,
  onSuccess(data) {
    today_stats.total_sold = data.total_sold
    today_stats.tickets_sold_today = data.tickets_sold_today
  },
  onError(error) {
    toast.error(error.message)
  },
})

const ticketSalesSeries = computed(() => {
  const series = ticket_insights.data?.ticket_sales_series
  return series?.length ? series : [{ key: 'tickets_sold', label: 'All tickets' }]
})

const ticketsSoldChartConfig = computed(() => {
  const showDataPoints = ticketSalesSeries.value.length === 1
  return {
    data: ticket_insights.data?.tickets_sold_over_time ?? [],
    title: '',
    xAxis: {
      key: 'date',
      type: 'time',
      timeGrain: 'day',
    },
    yAxis: {
      title: 'Tickets',
      yMin: 0,
      echartOptions: {
        minInterval: 1,
      },
    },
    series: ticketSalesSeries.value.map((series, index) => ({
      name: series.key,
      type: 'area',
      color: chartColors[index % chartColors.length],
      showDataPoints,
      fillOpacity: ticketSalesSeries.value.length > 1 ? 0.65 : 0.12,
      echartOptions: {
        name: series.label,
        stack: 'tickets',
      },
    })),
  }
})

const downloadFile = (contents, filename, type) => {
  const url = URL.createObjectURL(new Blob([contents], { type }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const downloadChartCsv = () => {
  const rows = ticket_insights.data?.tickets_sold_over_time ?? []
  const escapeCsv = (value) => {
    const stringValue = String(value)
    const sanitized = /^[=+\-@\t\r]/.test(stringValue) ? `'${stringValue}` : stringValue
    return `"${sanitized.replaceAll('"', '""')}"`
  }
  const csv = [
    ['Date', 'Total Tickets Purchased', ...ticketSalesSeries.value.map(({ label }) => label)]
      .map(escapeCsv)
      .join(','),
    ...rows.map((row) =>
      [row.date, row.tickets_sold, ...ticketSalesSeries.value.map(({ key }) => row[key] ?? 0)]
        .map(escapeCsv)
        .join(','),
    ),
  ].join('\n')
  downloadFile(csv, 'ticket-purchases-over-time.csv', 'text/csv;charset=utf-8')
}

const downloadChartPng = async (chartContainer) => {
  const svg = chartContainer?.querySelector('svg')
  if (!svg) {
    toast.error('The chart is not ready to download')
    return
  }

  const { width, height } = svg.getBoundingClientRect()
  const scale = 2
  const canvas = document.createElement('canvas')
  canvas.width = width * scale
  canvas.height = height * scale
  const context = canvas.getContext('2d')
  context.scale(scale, scale)
  context.fillStyle = '#ffffff'
  context.fillRect(0, 0, width, height)

  const svgUrl = URL.createObjectURL(
    new Blob([new XMLSerializer().serializeToString(svg)], { type: 'image/svg+xml' }),
  )
  const image = new Image()
  await new Promise((resolve, reject) => {
    image.onload = resolve
    image.onerror = reject
    image.src = svgUrl
  })
  context.drawImage(image, 0, 0, width, height)
  URL.revokeObjectURL(svgUrl)

  const pngBlob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'))
  if (pngBlob) {
    downloadFile(pngBlob, 'ticket-purchases-over-time.png', 'image/png')
  }
}

const ticket_checkin_insights = createResource({
  url: 'fossunited.api.tickets.get_checkin_insights',
  makeParams() {
    return {
      event_id: props.event.data.name,
    }
  },
  loading: true,
  auto: true,
  onError(error) {
    toast.error(error.message)
  },
})
</script>
