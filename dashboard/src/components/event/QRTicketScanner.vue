<template>
  <div
    v-if="modelValue"
    :class="[
      isFullscreen
        ? 'fixed inset-0 z-50 bg-black/90 flex items-center justify-center overflow-hidden p-4 md:p-8'
        : 'relative my-4 mx-auto border border-gray-300 w-full max-w-md',
    ]"
  >
    <!-- Close Button -->
    <button
      type="button"
      aria-label="Close scanner"
      title="Close"
      @click="emit('update:modelValue', false)"
      class="absolute top-3 right-3 z-50 grid place-items-center w-10 h-10 rounded-full bg-red-600/60 text-white text-xl hover:bg-black/70 focus:outline-none focus:ring-2 focus:ring-white/70"
    >
      <span aria-hidden="true">✕</span>
    </button>

    <!-- Camera wrapper with aspect ratio preserved -->
    <div
      :class="[
        isFullscreen
          ? 'w-[80vw] h-[80vh] max-w-[864px] aspect-video rounded-2xl'
          : 'w-full aspect-video rounded-xl',
      ]"
      class="relative bg-black"
    >
      <qrcode-stream
        :constraints="{ facingMode: 'environment' }"
        :paused="processing || !modelValue"
        @detect="onDetect"
        @camera-on="onCameraOn"
        @error="onError"
        class="absolute top-0 left-0 w-full h-full object-cover"
      />

      <!-- Corner overlay box -->
      <div
        v-if="showOverlay"
        class="absolute inset-0 flex items-center justify-center pointer-events-none z-20"
      >
        <div class="relative w-3/4 max-w-xs h-40">
          <div
            class="absolute top-0 left-0 w-6 h-6 border-t-4 border-l-4 border-green-400 rounded-tl-md"
          ></div>
          <div
            class="absolute top-0 right-0 w-6 h-6 border-t-4 border-r-4 border-green-400 rounded-tr-md"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-6 h-6 border-b-4 border-l-4 border-green-400 rounded-bl-md"
          ></div>
          <div
            class="absolute bottom-0 right-0 w-6 h-6 border-b-4 border-r-4 border-green-400 rounded-br-md"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { QrcodeStream } from 'vue-qrcode-reader'
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
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

function extractTicketId(input) {
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

  try {
    const scannedId = extractTicketId(rawValue)
    if (!scannedId || !/^[A-Za-z0-9_-]{6,}$/.test(scannedId)) {
      throw new Error('Invalid scanned ID')
    }
    emit('scanned', scannedId)
    emit('update:modelValue', false)
  } catch (err) {
    toast.error('Invalid QR code or format')
    processing.value = false
  }
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
