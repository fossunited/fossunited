<template>
  <button
    type="button"
    class="w-full flex justify-between px-7 py-3 bg-gray-900 text-white"
    :class="[
      'sticky z-30',
      view === 'vertical' ? 'top-12' : 'top-0',
      collapsible ? 'cursor-pointer' : 'cursor-default',
    ]"
    :aria-expanded="collapsible ? !isCollapsed : undefined"
    @click="collapsible && handleCollapse()"
    @keydown.enter.prevent="collapsible && handleCollapse()"
    @keydown.space.prevent="collapsible && handleCollapse()"
  >
    <h3 class="text-lg font-medium">{{ title }}</h3>
    <span v-if="collapsible" class="transition-transform" :class="isCollapsed ? 'rotate-180' : ''">
      <IconCaretDownFilled />
    </span>
  </button>
</template>

<script setup>
import { IconCaretDownFilled } from '@tabler/icons-vue'
import { defineProps, defineEmits, ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  collapsible: {
    type: Boolean,
    default: false,
  },
  view: {
    type: String,
    required: false,
    default: 'vertical',
  },
})

const emit = defineEmits(['collapse-hall'])
const isCollapsed = ref(false)

const handleCollapse = () => {
  const next = !isCollapsed.value
  isCollapsed.value = next
  emit('collapse-hall', next)
}
</script>
