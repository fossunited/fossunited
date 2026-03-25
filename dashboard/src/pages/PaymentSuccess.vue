<template>
  <Header />
  <canvas ref="confettiCanvas" class="fixed inset-0 pointer-events-none w-full h-full z-50" />
  <div class="w-full min-h-screen bg-surface-gray-1 flex justify-center items-start py-16 px-4">
    <div
      class="bg-surface-white border border-outline-gray-2 rounded-2xl px-10 py-10 flex flex-col gap-6 items-center max-w-md w-full shadow-sm"
    >
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
        <IconCircleCheck class="w-12 h-12 text-green-600" />
      </div>
      <div class="flex flex-col gap-2 text-center">
        <h1 class="text-2xl font-bold text-ink-gray-9">Payment Successful!</h1>
        <p class="text-sm text-ink-gray-5">
          Your tickets have been confirmed. Check your email for the confirmation and tickets.
        </p>
      </div>
      <div class="bg-surface-gray-1 rounded-lg px-5 py-4 w-full flex flex-col gap-2">
        <div class="flex justify-between text-sm">
          <span class="text-ink-gray-5">Order ID</span>
          <span class="font-mono text-ink-gray-8 text-xs">{{ orderId }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-ink-gray-5">Payment ID</span>
          <span class="font-mono text-ink-gray-8 text-xs">{{ paymentId }}</span>
        </div>
      </div>
      <p class="text-sm text-ink-gray-5 text-center">
        An invoice has been sent to your email address. For any assistance, email us at
        <a href="mailto:foundation@fossunited.org" class="underline font-medium"
          >foundation@fossunited.org</a
        >
      </p>
      <!-- Download Tickets — placeholder until PDF API is integrated -->
      <Button variant="outline" size="md" class="w-full" @click="downloadTickets">
        <span class="flex items-center justify-center gap-2">
          <IconDownload class="w-4 h-4" /> Download Tickets (PDF)
        </span>
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Button } from 'frappe-ui'
import Header from '@/components/Header.vue'
import { IconCircleCheck, IconDownload } from '@tabler/icons-vue'

const route = useRoute()
const orderId = route.query.order_id
const paymentId = route.query.payment_id
const confettiCanvas = ref(null)

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

function downloadTickets() {
  // TODO: Integrate with ticket PDF download API
  // Example: window.open(`/api/method/fossunited.api.tickets.download_ticket_pdf?order_id=${orderId}`)
  alert('PDF download will be available soon!')
}

onMounted(() => {
  launchConfetti()
})
</script>
