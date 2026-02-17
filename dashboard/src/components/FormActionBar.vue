<template>
  <Transition name="slide-up">
    <div
      v-if="hasChanges"
      class="fixed bottom-0 left-0 right-0 bg-surface-white border-t border-outline-gray-1 shadow-lg p-4 z-50"
      style="height: 56px"
    >
      <div
        class="max-w-7xl mx-auto grid grid-cols-[1fr_auto_auto] md:grid-cols-3 items-center gap-3 md:gap-4"
      >
        <div class="text-sm text-ink-gray-5">
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
import { toast } from 'vue-sonner'

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
    if (newDoc) {
      // Update original values when doc changes (includes after reload)
      if (Object.keys(originalData.value).length === 0) {
        originalData.value = JSON.parse(JSON.stringify(newDoc))
      }
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
  }, 300)
}

const handleCancel = () => {
  props.documentResource
    .reload()
    .then(() => {
      originalData.value = {}
      toast.info('Changes discarded')
      emit('cancel')
    })
    .catch((error) => {
      toast.error('Failed to discard changes ' + error)
    })
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
