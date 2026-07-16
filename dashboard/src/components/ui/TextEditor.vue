<template>
  <div class="flex flex-col gap-1">
    <div v-if="label" :id="labelId" class="text-base text-ink-gray-5">
      {{ label }}
      <span v-if="required" aria-hidden="true" class="text-red-500">*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </div>
    <FrappeTextEditor
      :content="modelValue"
      :placeholder="placeholder"
      :fixed-menu="menuButtons"
      :editable="!disabled"
      editor-class="w-full max-w-none min-h-[12rem] max-h-[48rem] overflow-y-auto border border-t-0 rounded-b-lg p-3"
      @change="emit('update:modelValue', $event)"
    />
    <small v-if="description" class="text-sm text-ink-gray-5">{{ description }}</small>
  </div>
</template>

<script setup>
import { getCurrentInstance } from 'vue'
import { TextEditor as FrappeTextEditor } from 'frappe-ui'

const uid = getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2, 7)
const labelId = `te-label-${uid}`

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  description: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

// Standard TipTap behavior: Enter = new paragraph, Shift+Enter = <br>
const starterkitOptions = {}
const extraExtensions = []

const menuButtons = [
  ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'Heading 5', 'Heading 6'],
  'Paragraph',
  'Separator',
  'Bold',
  'Italic',
  'Separator',
  'Bullet List',
  'Numbered List',
  'Task List',
  'Separator',
  'Align Left',
  'Align Center',
  'Align Right',
  'FontColor',
  'Separator',
  'Link',
  'Blockquote',
  'Code',
  'Horizontal Rule',
  [
    'InsertTable',
    'AddColumnBefore',
    'AddColumnAfter',
    'DeleteColumn',
    'AddRowBefore',
    'AddRowAfter',
    'DeleteRow',
    'MergeCells',
    'SplitCell',
    'ToggleHeaderColumn',
    'ToggleHeaderRow',
    'ToggleHeaderCell',
    'DeleteTable',
  ],
  'Separator',
  'Undo',
  'Redo',
]
</script>
