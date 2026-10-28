<template>
  <div class="flex flex-col gap-1">
    <div v-if="label" :id="labelId" class="text-base text-ink-gray-7 dark:text-ink-gray-8">
      {{ label }}
      <span v-if="required" aria-hidden="true" class="text-ink-red-4">*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </div>
    <Editor
      :model-value="modelValue"
      :extensions="extensions"
      :placeholder="placeholder"
      :editable="!disabled"
      :upload-function="publicUpload"
      @update:model-value="emit('update:modelValue', $event)"
    >
      <div class="rounded-6 border border-outline-gray-3">
        <EditorFixedMenu
          v-if="!disabled"
          class="flex-wrap border-b border-outline-gray-3 px-2 py-1.5"
          :items="toolbar"
        />
        <EditorTableMenu />
        <EditorContent
          :aria-labelledby="label ? labelId : undefined"
          :aria-describedby="description ? descriptionId : undefined"
          :aria-required="required || undefined"
          :class="editorClass"
        />
      </div>
    </Editor>
    <small
      v-if="description"
      :id="descriptionId"
      class="text-sm text-ink-gray-7 dark:text-ink-gray-8"
    >
      {{ description }}
    </small>
  </div>
</template>

<script setup>
import { upload } from 'frappe-ui'
import {
  Blockquote,
  Bold,
  BulletList,
  Editor,
  EditorContent,
  EditorFixedMenu,
  EditorTableMenu,
  H2,
  H3,
  H4,
  InsertLink,
  InsertTable,
  Italic,
  OrderedList,
  Paragraph,
  RichTextKit,
  Separator,
  Strike,
} from 'frappe-ui/editor'
import { computed, getCurrentInstance } from 'vue'

const uid = getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2, 7)
const labelId = `te-label-${uid}`
const descriptionId = `te-desc-${uid}`

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  description: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  // Taller editor for fields expected to hold longer content
  large: { type: Boolean, default: false },
})

const editorClass = computed(() => {
  const height = props.large ? 'min-h-[24rem]' : 'min-h-[12rem]'
  return `${height} max-h-[48rem] overflow-y-auto p-3`
})

const emit = defineEmits(['update:modelValue'])

const extensions = [RichTextKit]

// articleToolbar minus its HeadingGroup (which prints a static "Heading" label
// before its buttons) and InsertImage (images still go in by paste or drop).
const toolbar = [
  Paragraph,
  H2,
  H3,
  H4,
  Separator,
  Bold,
  Italic,
  Strike,
  Separator,
  BulletList,
  OrderedList,
  Blockquote,
  InsertLink,
  InsertTable,
]

// frappe-ui uploads pasted/dropped images as private by default. These
// editors feed public website pages (event/chapter descriptions etc.), so
// keep uploads public.
const publicUpload = (file, options) => upload(file, { ...options, private: false })
</script>
