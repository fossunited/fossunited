<template>
  <div
    v-if="modelValue"
    :class="[
      isFullscreen
        ? 'fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-surface-gray-10/90 p-4 md:p-8'
        : 'relative mx-auto my-4 w-full max-w-md border border-outline-gray-2',
    ]"
  >
    <!-- Close Button -->
    <button
      type="button"
      aria-label="Close scanner"
      title="Close"
      class="absolute right-3 top-3 z-50 grid h-10 w-10 place-items-center rounded-full bg-red-600/60 text-lg text-ink-base hover:bg-surface-gray-10/70 focus:outline-none focus:ring-2 focus:ring-white/70"
      @click="emit('update:modelValue', false)"
    >
      <span aria-hidden="true">✕</span>
    </button>

    <!-- Camera wrapper with aspect ratio preserved -->
    <div
      :class="[
        isFullscreen
          ? 'aspect-video h-[80vh] w-[80vw] max-w-[864px] rounded-8'
          : 'aspect-video w-full rounded-7',
      ]"
      class="relative bg-surface-gray-10"
    >
      <qrcode-stream
        :constraints="{ facingMode: 'environment' }"
        :paused="processing || !modelValue"
        class="absolute left-0 top-0 h-full w-full object-cover"
        @detect="onDetect"
        @camera-on="onCameraOn"
        @error="onError"
      />

      <!-- Corner overlay box -->
      <div
        v-if="showOverlay"
        class="pointer-events-none absolute inset-0 z-20 flex items-center justify-center"
      >
        <div class="relative h-40 w-3/4 max-w-xs">
          <div
            class="absolute left-0 top-0 h-6 w-6 rounded-tl-5 border-l-4 border-t-4 border-green-400"
          ></div>
          <div
            class="absolute right-0 top-0 h-6 w-6 rounded-tr-5 border-r-4 border-t-4 border-green-400"
          ></div>
          <div
            class="absolute bottom-0 left-0 h-6 w-6 rounded-bl-5 border-b-4 border-l-4 border-green-400"
          ></div>
          <div
            class="absolute bottom-0 right-0 h-6 w-6 rounded-br-5 border-b-4 border-r-4 border-green-400"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { QrcodeStream } from 'vue-qrcode-reader'
import { toast } from 'vue-sonner'

// Props
const props = defineProps({
  modelValue: Boolean,
  fullscreen: {
    type: Boolean,
    default: undefined,
  },
  showOverlay: {
    type: Boolean,
    default: true, // Show scan box by default
  },
})

const emit = defineEmits(['update:modelValue', 'scanned'])
const processing = ref(false)
const isMobile = ref(false)

const updateIsMobile = () => {
  isMobile.value = window.innerWidth < 768 // Tailwind 'md' breakpoint
}
onMounted(() => {
  updateIsMobile()
  window.addEventListener('resize', updateIsMobile, { passive: true })
})

const isFullscreen = computed(() => {
  return props.fullscreen !== undefined ? props.fullscreen : isMobile.value
})

function extractTicketId(input, depth = 0) {
  const s = String(input || '').trim()
  if (!s) return ''
  try {
    const u = new URL(s)
    const allowedHosts = ['fossunited.org', 'fossunited.com', 'fossunited.in']
    const host = u.hostname.toLowerCase()
    const isAllowed = allowedHosts.some((h) => host === h || host.endsWith('.' + h))
    if (!isAllowed) return ''
    const q =
      u.searchParams.get('ticket_id') ||
      u.searchParams.get('ticket') ||
      u.searchParams.get('id') ||
      u.searchParams.get('name')
    // Some printed tickets wrap the ticket URL inside ?id=; unwrap it once
    if (q && depth < 1 && /^https?:\/\//i.test(q)) return extractTicketId(q, depth + 1)
    if (q) return q
    const parts = u.pathname.split('/').filter(Boolean)
    return parts[parts.length - 1] || s
  } catch {
    return s
  }
}

function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue
  if (!rawValue || processing.value) return
  processing.value = true

  const scannedId = extractTicketId(rawValue)
  if (!scannedId || !/^[A-Za-z0-9_-]{6,}$/.test(scannedId)) {
    // Show what was read, so a wrong host or format is visible at the desk
    console.warn('[QRTicketScanner] unrecognised QR content:', rawValue)
    toast.error('Invalid QR code or format', { description: String(rawValue).slice(0, 120) })
    processing.value = false
    return
  }
  emit('scanned', scannedId)
  emit('update:modelValue', false)
}

function onCameraOn() {
  // Camera ready
}

function onError(error) {
  console.error('Camera error:', error)
  const map = {
    NotAllowedError: 'Camera permission denied',
    NotFoundError: 'No suitable camera found',
    NotSupportedError: 'HTTPS (or localhost) is required',
    NotReadableError: 'Camera is in use by another app',
    OverconstrainedError: 'Requested camera not available',
    StreamApiNotSupportedError: 'Browser lacks required APIs',
  }
  toast.error(map[error?.name] || `Camera error: ${error?.message || 'Unknown'}`)
  processing.value = false
  emit('update:modelValue', false)
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) processing.value = false
  },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateIsMobile)
})
</script>
<style scoped>
:deep(video) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
