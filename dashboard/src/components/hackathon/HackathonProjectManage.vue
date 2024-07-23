<template>
  <div class="flex flex-col gap-3">
    <div class="text-sm text-gray-600">
      Delete Project
    </div>
    <p class="text-base">Delete this project and create something new.</p>
    <Button
      icon-left="trash"
      label="Trash"
      theme="red"
      class="w-fit"
      @click="$emit('delete-project')"
    />
  </div>
</template>
<script setup>
import { defineEmits } from 'vue'

defineEmits(['delete-project'])
</script>
