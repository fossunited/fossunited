<template>
<Tooltip
    class="w-fit"
    :text="tooltip_label"
    :placement="'top'"
>
    <Button
        class="w-fit my-2 font-mono"
        size="md"
        icon-left="copy"
        @click="copyRouteToClipboard"
    >
    {{ props.route }}
    </Button>
</Tooltip>
</template>
<script setup>
import { Tooltip } from 'frappe-ui';
import { ref, defineProps } from 'vue'

let tooltip_label = ref('Copy to clipboard')

const props = defineProps({
    route: String
})
const copyRouteToClipboard = () => {
    navigator.clipboard.writeText(props.route)
    tooltip_label.value = 'Copied!'
    setTimeout(() => {
        tooltip_label.value = 'Copy to clipboard'
    }, 1000)
}
</script>
