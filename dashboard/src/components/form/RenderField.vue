<template>
  <!-- role="group" only wraps radio/multiselect where there are multiple controls -->
  <div
    :role="['radio_group', 'multiselect'].includes(field.fieldtype) ? 'group' : undefined"
    :aria-labelledby="
      ['radio_group', 'multiselect'].includes(field.fieldtype)
        ? `${field.fieldname}-label`
        : undefined
    "
  >
    <component
      :is="getComponent"
      v-model="fields[getFieldIndex(field.fieldname)]['value']"
      :label="field.label"
      :required="field.required"
      :type="field.fieldtype"
      variant="outline"
      :options="field.options || []"
      size="md"
      :aria-required="field.required ? 'true' : undefined"
      @blur="field.fieldtype === 'url' && normalizeUrl()"
    ></component>
    <p
      v-if="field.description"
      class="mt-1 text-sm text-ink-gray-5 prose max-w-none"
      v-html="markdownToHTML(field.description)"
    />
    <!-- hidden label for screen readers when no visible label -->
    <span
      v-if="['radio_group', 'multiselect'].includes(field.fieldtype)"
      :id="`${field.fieldname}-label`"
      class="sr-only"
    >
      {{ field.label || field.fieldname }}
    </span>
  </div>
</template>
<script setup>
import { FormControl } from 'frappe-ui'
import { computed, watch } from 'vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import RadioGroup from '@/components/ui/RadioGroup.vue'
import MultiselectInput from '@/components/ui/MultiselectInput.vue'
import { markdownToHTML } from 'frappe-ui/src/utils/markdown'
import { ensureHttpsPrefix } from '@/helpers/utils'

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

const normalizeUrl = () => {
  const idx = getFieldIndex(props.field.fieldname)
  if (idx !== -1) fields.value[idx].value = ensureHttpsPrefix(fields.value[idx].value)
}
</script>
