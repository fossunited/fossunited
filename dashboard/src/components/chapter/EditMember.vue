<template>
  <Dialog
    :options="{
      title: 'Edit Member',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-gray-700">Enter the new role of the member</div>
        <Select
          v-model="role"
          :options="[
            {
              label: 'Core Team Member',
              value: 'Core Team Member',
              disabled: !isCoreTeam,
            },
            {
              label: 'Volunteer',
              value: 'Volunteer',
            },
            {
              label: 'Graphic Designer',
              value: 'Graphic Designer',
            },
            {
              label: 'Content Writer',
              value: 'Content Writer',
            },
            {
              label: 'Marketing',
              value: 'Marketing',
            },
          ]"
          :multiple="false"
        >
        </Select>
      </div>
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-3">
        <Button label="Cancel" @click="$emit('close-dialog')" />
        <Button label="Edit" variant="solid" @click="$emit('update:edit-member', member, role)" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { Dialog, Select, createResource, Avatar } from 'frappe-ui'
import { ref, defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  chapter: {
    type: Object,
    default: () => null,
  },
  event: {
    type: Object,
    default: () => null,
  },
  member: {
    type: Object,
    default: () => null,
  },
  isCoreTeam: {
    type: Boolean,
    default: false,
  },
})

const emits = defineEmits(['update:edit-member', 'close-dialog'])

const role = ref('Volunteer')
</script>
