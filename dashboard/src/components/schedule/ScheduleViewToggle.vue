<template>
  <TabGroup :selected-index="tabIndex" @change="changeModelValue">
    <TabList class="flex gap-6">
      <Tab
        v-for="item in tabItems"
        :key="item.value"
        v-slot="{ selected }"
        class="focus-visible:outline-none"
      >
        <div
          class="border border-outline-gray-5 flex items-center justify-center p-2 text-base font-medium hover:bg-surface-gray-2 transition-colors"
          :class="{ 'bg-surface-gray-7 text-ink-white hover:bg-surface-gray-6': selected }"
        >
          <component :is="item.icon" :class="{ 'fill-white': selected }" />
        </div>
      </Tab>
    </TabList>
  </TabGroup>
</template>
<script setup>
import { defineModel, computed } from 'vue'
import { TabGroup, TabList, Tab } from '@headlessui/vue'
import { IconCarouselHorizontalFilled, IconCarouselVerticalFilled } from '@tabler/icons-vue'

const model = defineModel({
  prop: 'selectedScheduleView',
  event: 'change',
  type: String,
})

const changeModelValue = (index) => {
  model.value = tabItems[index].value
}

const tabItems = [
  {
    label: 'Vertical',
    icon: IconCarouselVerticalFilled,
    value: 'vertical',
  },
  {
    label: 'Horizontal',
    icon: IconCarouselHorizontalFilled,
    value: 'horizontal',
  },
]
const tabIndex = computed(() => tabItems.findIndex((item) => item.value === model.value))
</script>
