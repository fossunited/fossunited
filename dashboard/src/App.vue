<template>
  <div>
    <router-view v-slot="{ Component, route }">
      <component
        :is="Component"
        :key="route.name === 'Proposal Edit' ? route.fullPath : undefined"
      />
    </router-view>
    <Toaster rich-colors />
  </div>
</template>
<script setup>
import { Toaster } from 'vue-sonner'
</script>
