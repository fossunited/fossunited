<template>
  <div class="flex flex-col gap-2">
    <span v-if="label" :id="labelId" class="text-base text-ink-gray-5">
      {{ label }}
      <span v-if="required" aria-hidden="true" class="text-red-500">*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </span>
    <FileUploader
      :file-types="fileTypes"
      :upload-args="uploadArgs"
      :validate-file="validateFile"
      @success="handleSuccess"
      @failure="handleError"
    >
      <template #default="{ uploading, progress, openFileSelector, error }">
        <!-- Image Preview -->
        <div v-if="modelValue" class="mb-2">
          <img
            :src="modelValue"
            class="w-full h-40 object-contain rounded border bg-surface-gray-1"
            :alt="label ? `${label} preview` : 'Image preview'"
          />
          <div class="flex gap-2 mt-1.5">
            <button
              class="flex items-center gap-1 px-2 py-1 text-xs rounded bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3 transition-colors"
              :aria-label="`Change ${label || 'image'}`"
              @click="openFileSelector"
            >
              <IconEdit aria-hidden="true" class="w-3.5 h-3.5" />
              Change
            </button>
            <button
              class="flex items-center gap-1 px-2 py-1 text-xs rounded bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
              :aria-label="`Remove ${label || 'image'}`"
              @click="removeImage"
            >
              <IconTrash aria-hidden="true" class="w-3.5 h-3.5" />
              Remove
            </button>
          </div>
        </div>

        <!-- Upload Area -->
        <div
          v-else
          class="border-2 border-dashed rounded-lg p-8 transition-all duration-200"
          :class="uploading ? 'cursor-default' : 'hover:cursor-pointer focus:outline-2 focus:outline-offset-2'"
          role="button"
          tabindex="0"
          :aria-labelledby="label ? labelId : undefined"
          :aria-label="label ? undefined : 'Upload image'"
          :aria-describedby="description ? descriptionId : undefined"
          :aria-busy="uploading ? 'true' : undefined"
          :aria-disabled="uploading ? 'true' : undefined"
          @click="!uploading && openFileSelector()"
          @keydown.enter.prevent="!uploading && openFileSelector()"
          @keydown.space.prevent="!uploading && openFileSelector()"
        >
          <div v-if="uploading" class="flex flex-col items-center gap-2">
            <div
              role="progressbar"
              :aria-valuenow="progress"
              aria-valuemin="0"
              aria-valuemax="100"
              :aria-label="`Upload progress: ${progress}%`"
              class="w-full h-2 bg-surface-gray-3 rounded-full overflow-hidden"
            >
              <div
                class="h-full bg-surface-blue-3 transition-all duration-200"
                :style="{ width: `${progress}%` }"
              />
            </div>
            <span class="text-sm text-ink-gray-5" aria-live="polite" aria-atomic="true">
              Uploading... {{ progress }}%
            </span>
          </div>
          <div v-else class="flex flex-col items-center gap-3">
            <IconPhotoScan aria-hidden="true" class="w-8 h-8 text-ink-gray-3" />
            <p class="text-sm font-medium text-ink-gray-6">Click to browse files</p>
          </div>
        </div>

        <p
          v-if="error"
          role="alert"
          aria-live="assertive"
          class="mt-2 text-sm text-ink-red-4"
        >
          {{ error }}
        </p>
      </template>
    </FileUploader>
    <small
      v-if="description"
      :id="descriptionId"
      class="text-sm text-ink-gray-5"
    >
      {{ description }}
    </small>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FileUploader } from 'frappe-ui'
import { IconPhotoScan, IconTrash, IconEdit } from '@tabler/icons-vue'

const model = defineModel({ type: String, default: '' })

const props = defineProps({
  label: { type: String, default: '' },
  fileTypes: { type: [String, Array], default: 'image/*' },
  maxFileSize: { type: Number, default: 1.5 },
  maxWidth: { type: Number, default: null },
  maxHeight: { type: Number, default: null },
  description: { type: String, default: '' },
  required: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'error', 'uploaded'])

// Stable unique IDs for aria-labelledby / aria-describedby
const uid = Math.random().toString(36).slice(2, 8)
const labelId = `fua-label-${uid}`
const descriptionId = `fua-desc-${uid}`

const uploadArgs = computed(() => {
  const args = { optimize: true, private: false }
  if (props.maxWidth) args.max_width = props.maxWidth
  if (props.maxHeight) args.max_height = props.maxHeight
  return args
})

const validateFile = (file) => {
  if (!file.type.startsWith('image/')) {
    return 'Only image files are allowed'
  }
  if (file.size > props.maxFileSize * 1024 * 1024) {
    return `File size should not exceed ${props.maxFileSize}MB`
  }
  return null
}

const handleSuccess = (response) => {
  model.value = response.file_url
  emit('uploaded', response.file_url)
}

const handleError = (error) => {
  emit('error', error)
}

const removeImage = () => {
  model.value = ''
}
</script>
