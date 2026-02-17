<template>
  <TabGroup
    :class="{ hidden: dates.length <= 1 }"
    :selectedIndex="selectedIndex"
    @change="changeModelValue"
  >
    <TabList class="flex flex-wrap gap-5">
      <Tab
        v-for="(date, index) in dates"
        :key="date"
        v-slot="{ selected }"
        class="focus-visible:outline-none"
      >
        <div class="flex flex-col">
          <div class="bg-surface-gray-2 text-ink-gray-6 text-sm px-2 py-1 tracking-wider">
            {{ date }}
          </div>
        </div>
        <div
          class="border border-outline-gray-5 flex items-center justify-center p-2 text-base font-medium hover:bg-surface-gray-2 transition-colors"
          :class="{ 'bg-surface-gray-7 text-ink-white hover:bg-surface-gray-6': selected }"
        >
          Day {{ index + 1 }}
        </div>
      </Tab>
    </TabList>
  </TabGroup>
</template>
<script setup>
import { defineProps, defineModel, computed } from 'vue'
import { TabGroup, TabList, Tab } from '@headlessui/vue'

const props = defineProps({
  dates: {
    type: Array,
    required: true,
  },
})

const model = defineModel({
  prop: 'selectedDate',
  event: 'change',
  type: String,
})

const selectedIndex = computed(() => {
  const index = props.dates.findIndex((date) => date === model.value)
  return index !== -1 ? index : 0
})

function changeModelValue(index) {
  model.value = props.dates[index]
}
</script>
