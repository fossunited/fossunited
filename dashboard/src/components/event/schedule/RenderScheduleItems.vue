<script setup>
import ScheduleItem from './ScheduleItem.vue'
const emit = defineEmits(['modify-item'])
const schedule_items = defineModel('schedule', { type: Array, default: [] })
</script>
<template>
  <div class="flex flex-col gap-2">
    <div v-for="(item, index) in schedule_items" :key="item.idx" class="flex flex-col gap-2">
      <ScheduleItem v-model="schedule_items[index]" @click="emit('modify-item', item)" />
    </div>
  </div>
</template>
