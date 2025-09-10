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

// Parse and validate scanned QR content
function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue
  if (!rawValue) return
  if (processing.value) return
  processing.value = true

  if (import.meta?.env?.DEV) console.log('Scanned:', rawValue)

  let scannedId

  try {
    // Handle URL with ?id=...
    try {
      const url = new URL(rawValue)
      const allowedHosts = ['fossunited.org', 'fossunited.com']
      const isAllowed = allowedHosts.some(
        (h) => url.hostname === h || url.hostname.endsWith('.' + h),
      )
      if (isAllowed) {
        scannedId = url.searchParams.get('id') || url.searchParams.get('ticket') || undefined
      }
    } catch (e) {
      // Not a valid URL
    }

    // Fallback: allow raw alphanumeric IDs
    scannedId ||= /^[A-Za-z0-9_-]{6,}$/.test(rawValue) ? rawValue : undefined

    if (scannedId) {
      emit('update:props.modelValue', false) // Close scanner
      emit('scanned', scannedId) // Emit the scanned ID
    } else {
      toast.error('Invalid QR code')
      processing.value = false
    }
  } catch (err) {
    toast.error('Invalid QR code format')
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
