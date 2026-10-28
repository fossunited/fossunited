<template>
  <div
    class="rounded-6 border border-outline-gray-3 focus-within:ring-2 focus-within:ring-outline-gray-5"
  >
    <Editor
      ref="editorRef"
      :model-value="modelValue"
      :extensions="extensions"
      :upload-function="publicUpload"
      placeholder="Write a comment…"
      @update:model-value="emit('update:modelValue', $event)"
    >
      <template #default="{ isEmpty }">
        <EditorBubbleMenu :items="commentToolbar" />
        <EditorContent
          aria-label="Comment"
          class="max-h-[20rem] min-h-[6rem] overflow-y-auto px-3 py-2"
        />
        <div
          class="flex flex-wrap items-center justify-between gap-2 border-t border-outline-gray-3 px-2 py-1.5"
        >
          <EditorFixedMenu :items="commentToolbar" />
          <div class="flex gap-2">
            <Button
              size="sm"
              variant="ghost"
              label="Discard"
              :disabled="isEmpty"
              @click="discard"
            />
            <Button
              size="sm"
              variant="solid"
              :label="buttonLabel"
              :disabled="isEmpty"
              @click="submit"
            />
          </div>
        </div>
      </template>
    </Editor>
  </div>
</template>

<script setup>
import { Button, createResource, upload } from 'frappe-ui'
import {
  Editor,
  EditorContent,
  EditorFixedMenu,
  EditorBubbleMenu,
  CommentKit,
  commentToolbar,
} from 'frappe-ui/editor'
import { ref, inject } from 'vue'
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
const extensions = [CommentKit]
// frappe-ui uploads pasted images as private by default; keep them public so
// other reviewers can still see them.
const publicUpload = (file, options) => upload(file, { ...options, private: false })

const discard = () => {
  editorRef.value?.editor?.commands.clearContent()
}

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
