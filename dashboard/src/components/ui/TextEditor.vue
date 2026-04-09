<template>
  <div v-if="editor" class="flex flex-col gap-1 w-full">
    <TextEditorLinkDialog
      v-model:show="showDialog"
      v-model:link-data="linkData"
      v-model:editor="editor"
      @insert-link="handleLinkInsert(editor)"
    />
    <div :id="labelId" class="text-base text-ink-gray-5">
      {{ props.label }}
      <span v-if="required" aria-hidden="true" class="text-red-500">*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </div>
    <section
      role="toolbar"
      :aria-label="`${props.label || 'Text'} formatting`"
      :aria-controls="editorContentId"
      class="flex flex-wrap items-center gap-x-4 border-t border-l border-r border-outline-gray-1 buttons font-mono p-2"
    >
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :class="{ 'bg-surface-gray-3': editor.isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()" aria-label="Bold"
      >
        <IconBold class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'bg-surface-gray-3': editor.isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()" aria-label="Italic"
      >
        <IconItalic class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        :class="{ 'bg-surface-gray-3': editor.isActive('underline') }"
        @click="editor.chain().focus().toggleUnderline().run()" aria-label="Underline"
      >
        <IconUnderline class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        :class="{ 'bg-surface-gray-3': editor.isActive('strike') }"
        @click="editor.chain().focus().toggleStrike().run()" aria-label="Strikethrough"
      >
        <IconStrikethrough class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('paragraph') }"
        @click="editor.chain().focus().setParagraph().run()" aria-label="Paragraph"
      >
        <IconPilcrow class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('link') }"
        @click="handleToggleLink(editor)" aria-label="Insert link"
      >
        <IconLink class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 1 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" aria-label="Heading 1"
      >
        <IconH1 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 2 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" aria-label="Heading 2"
      >
        <IconH2 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 3 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" aria-label="Heading 3"
      >
        <IconH3 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 4 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 4 }).run()" aria-label="Heading 4"
      >
        <IconH4 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 5 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 5 }).run()" aria-label="Heading 5"
      >
        <IconH5 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-surface-gray-3': editor.isActive('heading', { level: 6 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 6 }).run()" aria-label="Heading 6"
      >
        <IconH6 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('bulletList') }"
        @click="editor.chain().focus().toggleBulletList().run()" aria-label="Bullet list"
      >
        <IconList class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('orderedList') }"
        @click="editor.chain().focus().toggleOrderedList().run()" aria-label="Ordered list"
      >
        <IconListNumbers class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('codeBlock') }"
        @click="editor.chain().focus().toggleCodeBlock().run()" aria-label="Code block"
      >
        <IconCode class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-surface-gray-3': editor.isActive('blockquote') }"
        @click="editor.chain().focus().toggleBlockquote().run()" aria-label="Blockquote"
      >
        <IconBlockquote class="w-5 h-5" />
      </button>
      <button class="p-1 rounded-sm" @click="editor.chain().focus().setHorizontalRule().run()" aria-label="Horizontal rule">
        <IconSeparatorHorizontal class="w-5 h-5" />
      </button>
    </section>
    <EditorContent :id="editorContentId" :editor="editor" :aria-labelledby="labelId" />
    <small :id="`${editorContentId}-desc`" class="text-sm text-ink-gray-5">{{ description }}</small>
  </div>
</template>
<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import Link from '@tiptap/extension-link'
import { defineProps, defineEmits, ref, reactive, watch, getCurrentInstance } from 'vue'
import {
  IconBold,
  IconItalic,
  IconUnderline,
  IconStrikethrough,
  IconLink,
  IconPilcrow,
  IconH1,
  IconH2,
  IconH3,
  IconH4,
  IconH5,
  IconH6,
  IconList,
  IconListNumbers,
  IconCode,
  IconBlockquote,
  IconSeparatorHorizontal,
} from '@tabler/icons-vue'
import TextEditorLinkDialog from './TextEditorLinkDialog.vue'

const uid = getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2, 7)
const labelId = `te-label-${uid}`
const editorContentId = `te-content-${uid}`

const showDialog = ref(false)
const linkData = reactive({
  previousText: '',
  previousValue: '',
  newText: '',
  newValue: '',
})
const emit = defineEmits(['update:modelValue'])

const props = defineProps({
  placeholder: {
    type: String,
    required: false,
    default: '',
  },
  modelValue: {
    /*
        modelValue is the v-model binding for the editor.
    */
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  description: {
    type: String,
    default: '',
  },
})

const editor = useEditor({
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    let html = editor.getHTML()
    // Replace comments anywhere in paragraphs
    html = html.replace(/<!--(.*?)-->/gs, '<span class="hidden-html-comment"><!--$1--></span>')
    emit('update:modelValue', html)
  },
  editorProps: {
    attributes: {
      class:
        'border border-outline-gray-1 rounded-sm max-w-none p-2 focus:outline-none min-h-[12rem] max-h-[48rem] overflow-y-auto focus:border-outline-gray-3 prose text-base resize-y',
      style: 'resize: vertical;',
    },
  },
  extensions: [
    StarterKit,
    Underline,
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
    Link.extend({ inclusive: false }).configure({
      protocols: ['ftp', 'mailto'],
      openOnClick: true,
      defaultProtocol: 'https',
      HTMLAttributes: {
        rel: 'noopener noreferrer',
        target: '_blank',
      },
    }),
  ],
})

watch(
  () => props.modelValue,
  (newValue) => {
    if (editor.value) {
      const currentContent = editor.value.getHTML()
      if (currentContent !== newValue) {
        editor.value.commands.setContent(newValue || '', false)
      }
    }
  },
)

const handleToggleLink = (editor) => {
  const selectedText = getSelectionText(editor)
  const selectedURL = editor.getAttributes('link').href || '' // Default to empty string

  linkData.previousText = selectedText
  linkData.previousValue = selectedURL
  linkData.newText = selectedText || ''
  linkData.newValue = selectedURL || ''
  showDialog.value = true
}

const getSelectionText = (editor) => {
  const { from, to, empty } = editor.state.selection

  if (empty) {
    return ''
  }

  return editor.state.doc.textBetween(from, to, ' ')
}

const handleLinkInsert = (editor) => {
  let { previousText, previousValue, newText, newValue } = linkData

  if (!newValue) {
    // Case 1: Remove link if URL is empty
    editor.chain().focus().extendMarkRange('link').unsetLink().run()
    showDialog.value = false
    resetLinkData()
    return
  }

  let allowedProtocols = ['http://', 'https://', 'mailto:']

  if (!allowedProtocols.some((proto) => newValue.startsWith(proto))) {
    newValue = `https://${newValue}`
  }

  if (previousText === newText && previousValue !== newValue) {
    // Case 2: Update only the URL
    editor.chain().focus().extendMarkRange('link').setLink({ href: newValue }).run()
    showDialog.value = false
    resetLinkData()
    return
  }

  // Case 3: Insert a new link or Change the text
  editor.chain().focus().extendMarkRange('link').unsetLink().run() // Clear any existing link formatting
  editor
    .chain()
    .focus()
    .insertContent(`<a href="${newValue}" target="_blank">${newText}</a>`, { parse: true })
    .run()

  showDialog.value = false
  resetLinkData()
}

const resetLinkData = () => {
  linkData.previousText = ''
  linkData.previousValue = ''
  linkData.newText = ''
  linkData.newValue = ''
}
</script>
