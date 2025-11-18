<template>
  <div role="group" :aria-labelledby="`${field.fieldname}-label`">
    <component
      :is="getComponent"
      v-model="fields[getFieldIndex(field.fieldname)]['value']"
      :label="field.label"
      :required="field.required"
      :type="field.fieldtype"
      variant="outline"
      :options="field.options || []"
      :description="field.description"
      size="md"
      :aria-required="field.required"
      :aria-describedby="field.description ? `${field.fieldname}-description` : undefined"
      :aria-invalid="hasError ? 'true' : 'false'"
      :aria-errormessage="hasError ? `${field.fieldname}-error` : undefined"
    ></component>
    <!-- hidden label for screen readers -->
    <label v-if="!field.label" :id="`${field.fieldname}-label`" class="sr-only">
      {{ field.fieldname }}
    </label>
    <!-- description for screen readers -->
    <span v-if="field.description" :id="`${field.fieldname}-description`" class="sr-only">
      {{ field.description }}
    </span>
    <!-- error message -->
    <span v-if="hasError" :id="`${field.fieldname}-error`" class="sr-only" role="alert">
      {{ errorMessage }}
    </span>
  </div>
</template>
<script setup>
import { FormControl } from 'frappe-ui'
import { computed, watch } from 'vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import RadioGroup from '@/components/ui/RadioGroup.vue'
import MultiselectInput from '@/components/ui/MultiselectInput.vue'

const props = defineProps({
  field: {
    type: Object,
    required: true,
  },
})

const fields = defineModel('fields', {
  type: Object,
  required: true,
})

const getComponent = computed(() => {
  switch (props.field.fieldtype) {
    case 'text_editor':
      return TextEditor
    case 'radio_group':
      return RadioGroup
    case 'multiselect':
      return MultiselectInput
    default:
      return FormControl
  }
})

const getFieldIndex = (fieldname) => {
  return fields.value.findIndex((field) => field.fieldname === fieldname)
}
</script>
