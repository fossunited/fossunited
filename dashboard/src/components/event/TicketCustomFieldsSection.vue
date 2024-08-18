<template>
  <TicketCustomFieldDialog
    :event="event"
    :inCreateMode="inCreateMode"
    :row="selectedRow"
    v-model="showDialog"
  />
  <div>
    <div class="prose">
      <h2 class="mb-1">Custom Fields</h2>
      <p class="text-sm">
        Any custom fields you want to collect while ticket booking
      </p>
      <Button
        variant="solid"
        label="Add Field"
        icon-left="plus"
        @click="handleCustomRowCreate"
      />
    </div>
    <ListView
      class="mt-4 min-h-[300px]"
      :columns="[
        {
          label: 'Field Label',
          key: 'label',
        },
        {
          label: 'Field Type',
          key: 'field_type',
        },
        {
          label: 'Is Mandatory?',
          key: 'mandatory',
        },
        {
          label: 'Fieldname',
          key: 'field_name',
        },
        {
          label: 'options',
          key: 'options',
        },
      ]"
      :rows="event.data.custom_fields"
      row-key="id"
      :options="{
        emptyState: {
          title: 'No Custom Fields',
          description: 'No custom fields have been added yet.',
        },
        selectable: false,
        showTooltip: true,
        resizeColumn: true,
        onRowClick: (row) => handleCustomRowEdit(row),
      }"
    >
      <template #cell="{ item, row, column }">
        <div v-if="column.key === 'mandatory'">
          <Checkbox :model-value="item" :disabled="true" />
        </div>
        <div v-else-if="column.key === 'field_name'">
          <span class="font-mono text-base">{{ item }}</span>
        </div>
        <div v-else-if="column.key === 'options' && key != null">
          <span class="text-sm">
            <span v-for="option in item.split('\n')" :key="option">
              <span class="px-1 py-0.5 bg-gray-200 rounded-sm mr-1">
                {{ option }}
              </span>
            </span>
          </span>
        </div>
        <div v-else>
          <span class="text-base">
            {{ item }}
          </span>
        </div>
      </template>
    </ListView>
  </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import { createResource, ListView, Checkbox } from 'frappe-ui'
import TicketCustomFieldDialog from '@/components/event/TicketCustomFieldDialog.vue'

const props = defineProps({
  event: {
    type: Object,
    default: null,
  },
})

const showDialog = ref(false)
const inCreateMode = ref(false)
const selectedRow = ref({})

const handleCustomRowEdit = (row) => {
  inCreateMode.value = false
  selectedRow.value = row
  showDialog.value = true
}

const handleCustomRowCreate = () => {
  selectedRow.value = {}
  inCreateMode.value = true
  showDialog.value = true
}
</script>
