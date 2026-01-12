<template>
  <Transition name="slide-up">
    <div
      v-if="showActions"
      class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg px-4 py-3 z-50"
      style="height: 56px"
    >
      <div
        class="max-w-7xl mx-auto grid grid-cols-[1fr_auto_auto] md:grid-cols-3 items-center gap-3 md:gap-4"
      >
        <div class="text-sm text-gray-600">
          <span class="font-medium">Unsaved changes</span>
        </div>
        <Button
          variant="subtle"
          size="md"
          class="md:w-full md:h-11"
          label="Cancel"
          @click="handleCancel"
        />
        <Button
          variant="solid"
          size="md"
          class="md:w-full md:h-11"
          label="Save Changes"
          :loading="isSaving"
          @click="handleSave"
        />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  hasChanges: {
    type: Boolean,
    required: true,
  },
  isSaving: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['save', 'cancel'])

const showActions = computed(() => props.hasChanges)

const handleSave = () => {
  emit('save')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    transform 0.3s ease,
    opacity 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-enter-to,
.slide-up-leave-from {
  transform: translateY(0);
  opacity: 1;
}
</style>
