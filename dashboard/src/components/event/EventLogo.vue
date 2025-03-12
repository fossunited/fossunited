<template>
  <div class="w-36 h-36 aspect-square border rounded p-3 flex items-center justify-center">
    <img :src="logoPath" alt="Event Logo" class="object-contain" />
  </div>
</template>
<script setup>
defineProps({
  logoPath: {
    type: String,
    required: true,
  },
})
</script>
