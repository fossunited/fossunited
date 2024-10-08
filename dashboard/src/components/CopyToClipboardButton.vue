<template>
  <Tooltip :text="tooltipText">
    <Button icon="copy" class="w-4" variant="ghost" @click="handleCopy" />
  </Tooltip>
</template>
<script setup>
import { Tooltip } from 'frappe-ui'
import { copyToClipboard } from '@/helpers/utils'
import { ref } from 'vue'

const tooltipText = ref('Copy to clipboard')

const props = defineProps({
  value: {
    type: String,
    required: true,
  },
})

const handleCopy = () => {
  copyToClipboard(props.value)
  tooltipText.value = 'Copied!'
  setTimeout(() => {
    tooltipText.value = 'Copy to clipboard'
  }, 1000)
}
</script>
