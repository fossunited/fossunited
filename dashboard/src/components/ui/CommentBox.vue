<template>
  <TextEditor
    ref="editorRef"
    editor-class="prose-sm max-w-none min-h-[6rem] max-h-[20rem] overflow-y-auto"
    :content="modelValue"
    placeholder="Write a comment…"
    @change="emit('update:modelValue', $event)"
  >
    <template #editor="{ editor }">
      <EditorContent
        class="border rounded-lg p-3 focus-within:ring-1 focus-within:ring-outline-gray-3"
        :editor="editor"
      />
    </template>

    <template #bottom>
      <div class="mt-2 flex items-center justify-between">
        <TextEditorFixedMenu class="-ml-1 overflow-x-auto" :buttons="menuButtons" />
        <Button :label="buttonLabel" variant="solid" @click="submit" />
      </div>
    </template>
  </TextEditor>
</template>

<script setup>
import { ref, inject } from 'vue'
import { EditorContent } from '@tiptap/vue-3'
import { Button, TextEditor, TextEditorFixedMenu, createResource } from 'frappe-ui'
import { toast } from 'vue-sonner'

const session = inject('$session')
const emit = defineEmits(['update:modelValue', 'commented'])

const props = defineProps({
  modelValue: { type: String, default: '' },
  hasCustomActions: { type: Boolean, default: false },
  customActions: { type: Array, default: () => [] },
  buttonLabel: { type: String, default: 'Comment' },
  doctype: { type: String, default: null },
  docname: { type: String, default: null },
})

const editorRef = ref(null)
const menuButtons = [
  'Bold',
  'Italic',
  'Strike',
  'Separator',
  'Bullet List',
  'Numbered List',
  'Separator',
  'Blockquote',
  'Code',
  'Link',
]

const submit = () => {
  if (props.hasCustomActions) {
    props.customActions.forEach((action) => action())
    emit('commented')
    return
  }
  defaultCommentAction()
}

const defaultCommentAction = () => {
  if (!props.doctype || !props.docname) {
    toast.error('Comment action failed, missing doctype or docname')
    return
  }

  const content = editorRef.value?.editor?.getHTML() ?? ''

  createResource({
    url: 'frappe.client.insert',
    makeParams() {
      return {
        doc: {
          doctype: 'Comment',
          comment_type: 'Comment',
          comment_email: session.user,
          reference_doctype: props.doctype,
          reference_docname: props.docname,
          content,
          ignore_permissions: true,
        },
      }
    },
    auto: true,
    onSuccess() {
      editorRef.value?.editor?.commands.clearContent()
      emit('commented')
    },
  })
}
</script>
