<template>
  <div
    class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 md:p-8 flex flex-col gap-6"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-1.5">
        <IconUserCircle class="w-6 h-6 text-ink-gray-7" />
        <span class="font-semibold text-ink-gray-9 tracking-tight">
          Attendee Details #{{ index + 1 }}
        </span>
      </div>
      <span
        class="bg-green-100 text-green-700 text-xs font-semibold tracking-wider uppercase px-3 py-1.5 rounded-lg"
      >
        {{ tierTitle }}
      </span>
      <button
        v-if="canDelete"
        class="bg-red-50 rounded-lg p-2.5 hover:bg-red-100 transition-colors"
        :aria-label="`Remove attendee #${index + 1}`"
        @click="$emit('delete')"
      >
        <IconTrash class="w-5 h-5 text-red-500" />
      </button>
    </div>

    <div class="flex flex-col gap-6">
      <FormControl
        :model-value="attendee.full_name"
        type="text"
        label="Name"
        size="sm"
        variant="subtle"
        placeholder="Full Name"
        required
        @update:model-value="update('full_name', $event)"
      />
      <FormControl
        :model-value="attendee.email"
        type="email"
        label="Email"
        size="sm"
        variant="subtle"
        placeholder="example@email.com"
        required
        @update:model-value="update('email', $event)"
      />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormControl
          :model-value="attendee.designation"
          type="text"
          label="Designation"
          size="sm"
          variant="subtle"
          placeholder="Designation"
          @update:model-value="update('designation', $event)"
        />
        <FormControl
          :model-value="attendee.organization"
          type="text"
          label="Institution"
          size="sm"
          variant="subtle"
          placeholder="Institution / College"
          @update:model-value="update('organization', $event)"
        />
      </div>

      <!-- Per-attendee custom fields -->
      <div v-if="customFields?.length" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormControl
          v-for="field in customFields"
          :key="field.name"
          :model-value="attendee.custom_fields?.[field.field_name]"
          :type="fieldTypeMap[field.field_type]"
          :label="field.label"
          :options="field.options"
          :required="field.mandatory"
          size="sm"
          variant="subtle"
          @update:model-value="updateCustomField(field.field_name, $event)"
        />
      </div>

      <!-- T-shirt -->
      <div v-if="showTshirt" class="flex items-center gap-4 flex-wrap">
        <FormControl
          :model-value="attendee.wants_tshirt"
          type="checkbox"
          size="sm"
          variant="subtle"
          label="I want a T-shirt"
          @update:model-value="update('wants_tshirt', $event)"
        />
        <div v-if="attendee.wants_tshirt" class="flex items-center gap-2">
          <FormControl
            :model-value="attendee.tshirt_size"
            type="select"
            :options="tshirtSizes"
            size="sm"
            variant="subtle"
            placeholder="Select size"
            required
            class="min-w-[110px]"
            @update:model-value="update('tshirt_size', $event)"
          />
          <span class="text-sm text-ink-gray-5">(+ ₹{{ tshirtPrice }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FormControl } from 'frappe-ui'
import { IconUserCircle, IconTrash } from '@tabler/icons-vue'

const props = defineProps({
  attendee: { type: Object, required: true },
  index: { type: Number, required: true },
  tierTitle: { type: String, default: '' },
  customFields: { type: Array, default: () => [] },
  showTshirt: { type: Boolean, default: false },
  tshirtPrice: { type: Number, default: 0 },
  canDelete: { type: Boolean, default: false },
})

const emit = defineEmits(['update:attendee', 'delete'])

const fieldTypeMap = { Data: 'text', Int: 'number', Select: 'select' }

const tshirtSizes = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL'].map((s) => ({
  label: s,
  value: s,
}))

function update(key, value) {
  emit('update:attendee', { ...props.attendee, [key]: value })
}

function updateCustomField(fieldName, value) {
  emit('update:attendee', {
    ...props.attendee,
    custom_fields: { ...props.attendee.custom_fields, [fieldName]: value },
  })
}
</script>
