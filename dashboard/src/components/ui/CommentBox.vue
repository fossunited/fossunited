<template>
  <div class="border rounded p-4 bg-surface-white w-full">
    <EditorContent :editor="editor" />
    <div class="flex justify-between items-center pt-2 mt-4">
      <div class="flex gap-1">
        <button
          class="p-1 rounded-sm"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :class="{ 'bg-surface-gray-3': editor.isActive('bold') }"
          @click="editor.chain().focus().toggleBold().run()"
        >
          <IconBold class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :class="{ 'bg-surface-gray-3': editor.isActive('italic') }"
          @click="editor.chain().focus().toggleItalic().run()"
        >
          <IconItalic class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :disabled="!editor.can().chain().focus().toggleUnderline().run()"
          :class="{ 'bg-surface-gray-3': editor.isActive('underline') }"
          @click="editor.chain().focus().toggleUnderline().run()"
        >
          <IconUnderline class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :disabled="!editor.can().chain().focus().toggleStrike().run()"
          :class="{ 'bg-surface-gray-3': editor.isActive('strike') }"
          @click="editor.chain().focus().toggleStrike().run()"
        >
          <IconStrikethrough class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :class="{ 'bg-surface-gray-3': editor.isActive('bulletList') }"
          @click="editor.chain().focus().toggleBulletList().run()"
        >
          <IconList class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :class="{ 'bg-surface-gray-3': editor.isActive('orderedList') }"
          @click="editor.chain().focus().toggleOrderedList().run()"
        >
          <IconListNumbers class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <button
          class="p-1 rounded-sm"
          :class="{ 'bg-surface-gray-3': editor.isActive('blockquote') }"
          @click="editor.chain().focus().toggleBlockquote().run()"
        >
          <IconBlockquote class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
      </div>
      <Button :label="buttonLabel" variant="solid" @click="submit" />
    </div>
  </div>
</template>

<script setup>
import {
  IconBold,
  IconItalic,
  IconUnderline,
  IconStrikethrough,
  IconList,
  IconListNumbers,
  IconBlockquote,
} from '@tabler/icons-vue'
import { ref, onBeforeUnmount, inject } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { toast } from 'vue-sonner'
import { createResource } from 'frappe-ui'

const session = inject('$session')
const emit = defineEmits(['update:modelValue', 'commented'])

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  hasCustomActions: {
    type: Boolean,
    default: false,
  },
  customActions: {
    type: Array,
    default: () => [],
  },
  buttonLabel: {
    type: String,
    default: 'Comment',
  },
  doctype: {
    type: String,
    default: null,
  },
  docname: {
    type: String,
    default: null,
  },
})

const editor = new Editor({
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  editorProps: {
    attributes: {
      class: 'w-full h-[6rem] focus:outline-none prose prose-sm overflow-y-auto',
      placeholder: 'Write a comment…',
    },
  },
  extensions: [
    StarterKit,
    Underline,
    Placeholder.configure({
      placeholder: 'Write a comment…',
    }),
  ],
})

onBeforeUnmount(() => {
  editor.destroy()
})

const submit = () => {
  if (!props.hasCustomActions) {
    defaultCommentAction()
    emit('commented')
    return
  }

  props.customActions.forEach((action) => {
    action()
    emit('commented')
  })
}

const defaultCommentAction = () => {
  if (!props.doctype || !props.docname) {
    toast.error('Comment action failed, missing doctype or docname')
    return
  }

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
          content: editor.getHTML(),
          ignore_permissions: true,
        },
      }
    },
    auto: true,
    onSuccess() {
      editor.commands.clearContent()
      emit('commented')
    },
  })
}

const buttonClass = (isActive) =>
  `px-2 py-1 text-sm rounded ${isActive ? 'bg-surface-gray-3' : 'hover:bg-surface-gray-2'}`
</script>
