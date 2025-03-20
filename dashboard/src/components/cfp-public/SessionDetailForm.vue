<template>
  <div class="flex flex-col gap-8 w-full p-8 border rounded bg-white">
    <h4 class="flex gap-2 items-center font-semibold">
      <IconClipboardText />
      <span>Submission Form</span>
    </h4>
    <RenderField
      v-for="(_field, index) in fields"
      :key="index"
      v-model:fields="fields"
      :field="_field"
    />
    <ReferencesComponent v-model:references="references" />
  </div>
</template>
<script setup>
import RenderField from '@/components/form/RenderField.vue'
import ReferencesComponent from '@/components/cfp-public/ReferencesComponent.vue'
import { IconClipboardText } from '@tabler/icons-vue'

const fields = defineModel('fields', {
  type: Array,
  required: true,
})

const references = defineModel('references', {
  type: Array,
  required: true,
})
</script>
