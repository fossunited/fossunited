<template>
  <div
    class="w-auto flex justify-between px-7 py-3 bg-gray-900 text-white cursor-pointer"
    :class="['sticky z-30', view === 'vertical' ? 'top-12' : 'top-0']"
    @click="collapsible && handleCollapse()"
  >
    <h3 class="text-lg font-medium">{{ title }}</h3>
    <span v-if="collapsible" class="transition-transform" :class="isCollapsed ? 'rotate-180' : ''">
      <IconCaretDownFilled />
    </span>
  </div>
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
    required: true,
    default: 'vertical',
  },
})

const emit = defineEmits(['collapse-hall'])
const isCollapsed = ref(false)

const handleCollapse = () => {
  emit('collapse-hall')
  isCollapsed.value = !isCollapsed.value
}
</script>
