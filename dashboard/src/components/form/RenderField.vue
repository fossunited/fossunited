<template>
  <div>
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
    ></component>
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
