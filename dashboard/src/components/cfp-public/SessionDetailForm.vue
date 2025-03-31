<template>
  <div class="flex flex-col gap-8 w-full p-4 md:p-8 border rounded bg-white">
    <h4 class="flex gap-2 items-center font-semibold">
      <IconClipboardText />
      <span>Submission Form</span>
    </h4>
    <RenderField
      v-for="(_field, index) in fields"
      :id="`${_field.fieldname}_field`"
      :key="index"
      v-model:fields="fields"
      :field="_field"
      :class="{ hidden: _field.fieldname === 'other_category' }"
    />
    <ReferencesComponent v-model:references="references" />
  </div>
</template>
<script setup>
import { watch } from 'vue'
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

// Watch to show or hide the other category field based on session categories
watch(
  () => fields.value,
  (newVal) => {
    if (newVal) {
      const otherCategory = newVal.find((field) => field.fieldname === 'other_category')
      const categories = newVal.find((field) => field.fieldname === 'session_categories')

      if (categories.value.includes('Other')) {
        let otherCategoryDiv = document.getElementById(`${otherCategory.fieldname}_field`)
        otherCategoryDiv.classList.remove('hidden')
      }

      if (!categories.value.includes('Other')) {
        let otherCategoryDiv = document.getElementById(`${otherCategory.fieldname}_field`)
        otherCategoryDiv.classList.add('hidden')
      }
    }
  },
  { deep: true },
)

// mechanism to add new category to session categories
watch(
  () => fields.value,
  (newVal) => {
    if (newVal) {
      const otherCategory = newVal.find((field) => field.fieldname === 'other_category')
      const categories = newVal.find((field) => field.fieldname === 'session_categories')

      if (otherCategory.value) {
        if (otherCategory.value && otherCategory.value.endsWith('\n')) {
          const newCategory = otherCategory.value.trim()
          categories.options.push({
            label: newCategory,
            value: newCategory,
          })
          categories.value.push(newCategory)
          otherCategory.value = '' // Clear the input after adding
        }
      }
    }
  },
  { deep: true },
)
</script>
