<template>
    <div>
        <h1>Event: {{ route.params.id }}</h1>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>
