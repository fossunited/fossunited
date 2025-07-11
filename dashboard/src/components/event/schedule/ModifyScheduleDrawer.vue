<script setup>
import Drawer from '@/components/ui/Drawer.vue'
import ModifyScheduleItem from './ModifyScheduleItem.vue'

const show = defineModel('show', { type: Boolean })
const scheduleItem = defineModel({ type: Object })
const emit = defineEmits(['update:schedule', 'delete:schedule'])
</script>
<template>
  <Drawer v-model="show">
    <ModifyScheduleItem
      v-model="scheduleItem"
      @update:schedule="emit('update:schedule')"
      @delete:schedule="emit('delete:schedule', $event)"
    />
  </Drawer>
</template>
