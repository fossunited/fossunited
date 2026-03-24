<template>
  <div class="flex mt-4 w-full gap-4 transition-all" :class="navigationAlignment">
    <Button
      v-if="showBackButton"
      label="Back"
      size="lg"
      variant="subtle"
      icon-left="chevron-left"
      class="uppercase !min-w-8 !font-medium !pr-4"
      @click="$emit('back')"
    />
    <Button
      :label="actionButtonLabel"
      size="lg"
      variant="solid"
      :icon-right="!isLastStep ? 'chevron-right' : ''"
      class="uppercase !min-w-8 !font-medium !px-4"
      :loading="loading"
      :disabled="loading"
      @click="handleActionClick"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  isFirstStep: {
    type: Boolean,
    default: false,
  },
  isLastStep: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  labels: {
    type: Object,
    default: () => ({
      first: 'Apply Now',
      next: 'Next',
      submit: 'Submit',
    }),
  },
})

const emits = defineEmits(['back', 'next', 'submit'])

// Computed properties for cleaner template
const navigationAlignment = computed(() => (props.isFirstStep ? 'justify-center' : 'justify-end'))

const showBackButton = computed(() => !props.isFirstStep)

const actionButtonLabel = computed(() => {
  if (props.isFirstStep) return props.labels.first
  if (props.isLastStep) return props.labels.submit
  return props.labels.next
})

// Handle click based on the current step
const handleActionClick = () => {
  if (props.loading) return
  if (props.isLastStep) {
    emits('submit')
  } else {
    emits('next')
  }
}
</script>
