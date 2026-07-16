<template>
  <Header />
  <canvas ref="confettiCanvas" class="fixed inset-0 pointer-events-none w-full h-full z-50" />

  <div class="bg-surface-gray-1 min-h-screen">
    <main class="max-w-[600px] mx-auto w-full flex flex-col gap-6 py-8 px-4 pb-24">
      <EventHeader v-if="event.data" :event="event.data" />

      <div
        class="bg-surface-white border border-outline-gray-2 rounded-2xl p-8 flex flex-col gap-6 items-center text-center"
      >
        <div class="w-20 h-20 bg-surface-green-2 rounded-full flex items-center justify-center">
          <IconCircleCheck class="w-12 h-12 text-ink-green-3" />
        </div>

        <div class="flex flex-col gap-2">
          <h1 class="text-2xl font-bold text-ink-gray-9">Payment Successful!</h1>
          <p class="text-sm text-ink-gray-5">
            Your tickets are confirmed. Check your email for the confirmation.
          </p>
          <p v-if="event.data" class="text-sm font-medium text-ink-gray-7 mt-1">
            We are eagerly looking forward to seeing you at
            <span class="text-ink-gray-9 font-semibold">{{ event.data.event_name }}</span
            >!
          </p>
        </div>

        <!-- Order summary -->
        <div class="bg-surface-gray-1 rounded-lg px-5 py-4 w-full flex flex-col gap-2 text-left">
          <div class="flex justify-between text-sm">
            <span class="text-ink-gray-5">Order ID</span>
            <span class="font-mono text-ink-gray-8 text-xs">{{ orderId }}</span>
          </div>
          <div v-if="ticketCount !== null" class="flex justify-between text-sm">
            <span class="text-ink-gray-5">Tickets</span>
            <span class="font-medium text-ink-gray-8">
              {{ ticketCount }} ticket{{ ticketCount !== 1 ? 's' : '' }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col gap-3 w-full">
          <Button
            variant="solid"
            size="md"
            class="w-full"
            :loading="downloading"
            @click="downloadAll"
          >
            <span class="flex items-center justify-center gap-2">
              <IconDownload class="w-4 h-4" /> Download Tickets (PDF)
            </span>
          </Button>
          <Button
            variant="subtle"
            size="md"
            class="w-full"
            :loading="previewing"
            @click="togglePreview"
          >
            <span class="flex items-center justify-center gap-2">
              <IconEye class="w-4 h-4" />
              {{ pdfPreviewUrl ? 'Hide Preview' : 'Preview Ticket' }}
            </span>
          </Button>
        </div>

        <!-- Inline PDF preview -->
        <div
          v-if="pdfPreviewUrl"
          class="w-full rounded-xl overflow-hidden border border-outline-gray-2"
        >
          <iframe
            :src="pdfPreviewUrl"
            class="w-full"
            style="height: 560px"
            title="Ticket Preview"
          />
        </div>

        <p class="text-xs text-ink-gray-4">
          For any assistance, email
          <a :href="`mailto:${contactEmail}`" class="underline">{{ contactEmail }}</a>
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import Header from '@/components/Header.vue'
import EventHeader from '@/components/common/EventHeader.vue'
import { IconCircleCheck, IconDownload, IconEye } from '@tabler/icons-vue'
import { showError } from '@/helpers/utils'

const route = useRoute()
const orderId = route.query.order_id
const eventId = route.query.event

const confettiCanvas = ref(null)
const ticketCount = ref(null)
const ticketIds = ref([])
const downloading = ref(false)
const previewing = ref(false)
const pdfPreviewUrl = ref(null)

const event = createResource({
  url: 'fossunited.api.dashboard.get_event',
  makeParams: () => ({ name: eventId }),
  auto: Boolean(eventId),
})

const contactEmail = computed(
  () => event.data?.chapter_email || 'indiafoss@fossunited.org',
)

const tickets = createResource({
  url: 'fossunited.api.tickets.search_tickets',
  makeParams: () => ({ search_term: orderId }),
  auto: Boolean(orderId) && !orderId.startsWith('MOCK'),
  onSuccess(data) {
    ticketIds.value = (data || []).map((t) => t.name)
    ticketCount.value = ticketIds.value.length
  },
  onError(err) {
    showError(err, 'Could not load tickets')
  },
})

// Auto-load preview once ticket IDs arrive
watch(ticketIds, (ids) => {
  if (ids.length > 0 && !pdfPreviewUrl.value) loadPreview()
})

function apiUrl() {
  if (ticketIds.value.length === 1) {
    return `/api/method/fossunited.api.tickets.download_ticket?ticket_id=${encodeURIComponent(ticketIds.value[0])}`
  }
  return `/api/method/fossunited.api.tickets.download_all_tickets?ticket_ids=${encodeURIComponent(JSON.stringify(ticketIds.value))}`
}

async function loadPreview() {
  if (previewing.value || ticketIds.value.length === 0) return
  previewing.value = true
  try {
    const res = await fetch(apiUrl())
    if (!res.ok) throw new Error('Failed to fetch PDF')
    const blob = await res.blob()
    if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
    pdfPreviewUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    showError(err, 'Could not preview ticket')
  } finally {
    previewing.value = false
  }
}

function togglePreview() {
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value)
    pdfPreviewUrl.value = null
  } else {
    loadPreview()
  }
}

function downloadAll() {
  if (downloading.value || ticketIds.value.length === 0) return
  downloading.value = true
  try {
    const a = document.createElement('a')
    a.href = apiUrl()
    a.download = 'tickets.pdf'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } finally {
    downloading.value = false
  }
}

function launchConfetti() {
  const canvas = confettiCanvas.value
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  const ctx = canvas.getContext('2d')
  const colors = ['#4ade80', '#22c55e', '#16a34a', '#facc15', '#f97316', '#60a5fa', '#c084fc']
  const particles = Array.from({ length: 180 }, () => ({
    x: Math.random() * canvas.width,
    y: -Math.random() * canvas.height * 0.5,
    w: Math.random() * 10 + 5,
    h: Math.random() * 6 + 3,
    color: colors[Math.floor(Math.random() * colors.length)],
    vx: (Math.random() - 0.5) * 3,
    vy: Math.random() * 4 + 2,
    angle: Math.random() * 360,
    spin: (Math.random() - 0.5) * 6,
    gravity: 0.12,
  }))
  let frame = 0
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    for (const p of particles) {
      p.x += p.vx
      p.vy += p.gravity
      p.y += p.vy
      p.angle += p.spin
      ctx.save()
      ctx.translate(p.x + p.w / 2, p.y + p.h / 2)
      ctx.rotate((p.angle * Math.PI) / 180)
      ctx.fillStyle = p.color
      ctx.globalAlpha = Math.max(0, 1 - frame / 200)
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h)
      ctx.restore()
    }
    frame++
    if (frame < 220) requestAnimationFrame(animate)
    else ctx.clearRect(0, 0, canvas.width, canvas.height)
  }
  animate()
}

onMounted(launchConfetti)
</script>
