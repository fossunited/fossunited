<template>
  <div>
    <router-view />
    <Toaster rich-colors />
  </div>
</template>
<script setup>
import { Toaster } from 'vue-sonner'
</script>
