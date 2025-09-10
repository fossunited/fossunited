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
import { ref } from 'vue'

// Props
defineProps({
  modelValue: Boolean, // for v-model: show/hide
})

// Emits
const emit = defineEmits(['update:modelValue', 'scanned'])

// Parse and validate scanned QR content
function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue
  if (!rawValue) return

  if (import.meta?.env?.DEV) console.log('Scanned:', rawValue)

  let scannedId

  try {
    // Handle URL with ?id=...
    try {
      const url = new URL(rawValue)
      const allowed = /\.?fossunited\./.test(url.hostname)
      scannedId = allowed ? url.searchParams.get('id') || undefined : undefined
    } catch (e) {
      // Not a valid URL
    }

    // Fallback: allow raw alphanumeric IDs
    scannedId ||= /^[A-Za-z0-9_-]+$/.test(rawValue) ? rawValue : undefined

    if (scannedId) {
      emit('update:modelValue', false) // Close scanner
      emit('scanned', scannedId) // Emit the scanned ID
    } else {
      alert('Invalid QR code')
    }
  } catch (err) {
    alert('Invalid QR code format')
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
  alert(map[error?.name] || `Camera error: ${error?.message || 'Unknown'}`)
  emit('update:modelValue', false)
}
</script>
