<template>
<div class="relative flex px-4 py-6 h-screen w-1/5 border-r flex-col justify-between transition-all duration-300 ease-in-out" id="sidebar">
    <div class="font-fff text-sm leading-relaxed">
        {{ props.title }}
    </div>
</div>
</template>

<script setup>
const props = defineProps({
    title: {
        type: String,
        default: "Organizer Dashboard",
    }
})
</script>
