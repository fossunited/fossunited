<template>
  <div
    v-if="modelValue"
    class="my-4 mx-auto border border-gray-300"
    :style="{ width: '100%', maxWidth: '24rem' }"
  >
    <qrcode-stream
      :constraints="{ facingMode: 'environment' }"
      @detect="onDetect"
      @camera-on="onCameraOn"
      @error="onError"
    />
  </div>
</template>

<script setup>
import { QrcodeStream } from 'vue-qrcode-reader'
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'

// Props
const props = defineProps({
  modelValue: Boolean,
})

// Emits
const emit = defineEmits(['update:props.modelValue', 'scanned'])
const processing = ref(false)

function extractTicketId(input) {
  const s = String(input || '').trim()
  if (!s) return ''
  try {
    const u = new URL(s)
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

// Parse and validate scanned QR content
function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue
  if (!rawValue) return
  if (processing.value) return
  processing.value = true

  if (import.meta?.env?.DEV) console.log('Scanned:', rawValue)

  let scannedId

  try {
    scannedId = extractTicketId(rawValue)

    // Optionally validate scannedId format here, e.g. alphanumeric min length
    if (!scannedId || !/^[A-Za-z0-9_-]{6,}$/.test(scannedId)) {
      throw new Error('Invalid scanned ID format')
    }

    emit('update:props.modelValue', false) // Close scanner
    emit('scanned', scannedId) // Emit normalized ID
  } catch (err) {
    toast.error('Invalid QR code or format')
    processing.value = false
  }
}

// Optional: camera success hook
function onCameraOn() {
  // Add torch support or loading state if needed
}

// Handle camera access errors
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
  emit('update:props.modelValue', false)
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      // Reset internal state each time scanner is shown
      processing.value = false
    }
  },
)
</script>
