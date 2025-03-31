<template>
  <AccordionRoot>
    <template v-for="(item, index) in accordianItems" :key="index">
      <AccordionItem :value="item.value">
        <AccordionHeader>
          <AccordionTrigger>
            <IconChevronDown class="w-4 h-4" />
            <slot name="title">
              {{ item.title }}
            </slot>
          </AccordionTrigger>
        </AccordionHeader>
        <AccordionContent>
          <slot name="content">
            {{ item.content }}
          </slot>
        </AccordionContent>
      </AccordionItem>
    </template>
  </AccordionRoot>
</template>
<script setup>
import { IconChevronDown } from '@tabler/icons-vue'
import {
  AccordionContent,
  AccordionHeader,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
} from 'radix-vue'

defineProps({
  accordianItems: {
    type: Array,
    required: false,
    default: () => [],
  },
})
</script>
