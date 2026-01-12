<template>
  <Transition name="slide-up">
    <div
      v-if="hasChanges"
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
import { ref, computed, watch } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  documentResource: {
    type: Object,
    required: true, // only DocumentResource
  },
  isSaving: {
    type: Boolean,
    default: false,
  },
  fieldsToWatch: {
    type: Array,
    default: null, // If null, watch all fields
  },
})

const emit = defineEmits(['save', 'cancel'])

const originalData = ref({})

// Watch the document and store original values
watch(
  () => props.documentResource.doc,
  (newDoc) => {
    if (newDoc && Object.keys(originalData.value).length === 0) {
      // Store initial values
      originalData.value = JSON.parse(JSON.stringify(newDoc))
    }
  },
  { immediate: true, deep: true },
)

// Detect changes
const hasChanges = computed(() => {
  if (!props.documentResource.doc || !originalData.value) return false

  const fieldsToCheck = props.fieldsToWatch || Object.keys(originalData.value)

  return fieldsToCheck.some((key) => {
    return (
      JSON.stringify(props.documentResource.doc[key]) !== JSON.stringify(originalData.value[key])
    )
  })
})

const handleSave = () => {
  emit('save')
  // Reset original data after save
  setTimeout(() => {
    if (props.documentResource.doc) {
      originalData.value = JSON.parse(JSON.stringify(props.documentResource.doc))
    }
  }, 100)
}

const handleCancel = () => {
  // Reload the document to discard changes
  props.documentResource.reload()
  // Reset original data
  originalData.value = {}
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
