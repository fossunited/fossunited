<template>
  <TabGroup @change="changeModelValue" :class="{ hidden: dates.length <= 1 }">
    <TabList class="flex flex-wrap gap-5">
      <Tab
        v-for="(date, index) in dates"
        :key="date"
        v-slot="{ selected }"
        class="focus-visible:outline-none"
      >
        <div class="flex flex-col">
          <div class="bg-gray-100 text-gray-700 text-sm px-2 py-1 tracking-wider">
            {{ date }}
          </div>
        </div>
        <div
          class="border border-gray-900 flex items-center justify-center p-2 text-base font-medium hover:bg-gray-100 transition-colors"
          :class="{ 'bg-gray-900 text-white hover:bg-gray-800': selected }"
        >
          Day {{ index + 1 }}
        </div>
      </Tab>
    </TabList>
  </TabGroup>
</template>
<script setup>
import { defineProps, defineModel } from 'vue'
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
})

function changeModelValue(index) {
  model.value = props.dates[index]
}
</script>
