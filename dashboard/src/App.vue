<template>
  <div>
    <router-view />
    <Toaster richColors />
  </div>
</template>
<script setup>
import { Toaster } from 'vue-sonner'
</script>
