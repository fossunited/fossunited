<template>
  <div class="flex flex-col gap-4 bg-surface-white w-full p-8 border rounded items-center">
    <IconCircleCheckFilled class="w-16 h-16 fill-green-500" />

    <div class="prose-sm text-center">
      <h3>You have successfully submitted your proposal!</h3>
      <p>We will review your proposal and get back to you soon.</p>
      <p>Check your email for updates.</p>
      <p>
        You can also view your submissions on the
        <RouterLink to="/my-proposals" class="underline"> submission dashboard </RouterLink>
      </p>
    </div>
  </div>
</template>
<script setup>
import { IconCircleCheckFilled } from '@tabler/icons-vue'
</script>
