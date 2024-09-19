<template>
  <div v-if="editor" class="flex flex-col gap-1">
    <div class="text-base text-gray-600">{{ props.label }}</div>
    <section
      class="flex flex-wrap items-center gap-x-4 border-t border-l border-r border-gray-200 buttons font-mono p-2"
    >
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :class="{ 'bg-gray-200': editor.isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-bold"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M7 5h6a3.5 3.5 0 0 1 0 7h-6z" />
          <path d="M13 12h1a3.5 3.5 0 0 1 0 7h-7v-7" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'bg-gray-200': editor.isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-italic"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M11 5l6 0" />
          <path d="M7 19l6 0" />
          <path d="M14 5l-4 14" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        :class="{ 'bg-gray-200': editor.isActive('underline') }"
        @click="editor.chain().focus().toggleUnderline().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#000000"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-underline"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M7 5v5a5 5 0 0 0 10 0v-5" />
          <path d="M5 19h14" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        :class="{ 'bg-gray-200': editor.isActive('strike') }"
        @click="editor.chain().focus().toggleStrike().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-strikethrough"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M5 12l14 0" />
          <path
            d="M16 6.5a4 2 0 0 0 -4 -1.5h-1a3.5 3.5 0 0 0 0 7h2a3.5 3.5 0 0 1 0 7h-1.5a4 2 0 0 1 -4 -1.5"
          />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('paragraph') }"
        @click="editor.chain().focus().setParagraph().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-section-sign"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M9.172 19a3 3 0 1 0 2.828 -4" />
          <path d="M14.83 5a3 3 0 1 0 -2.83 4" />
          <path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 1 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-1"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M19 18v-8l-2 2" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 2 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-2"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M17 12a2 2 0 1 1 4 0c0 .591 -.417 1.318 -.816 1.858l-3.184 4.143l4 0" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 3 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-3"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M19 14a2 2 0 1 0 -2 -2" />
          <path d="M17 16a2 2 0 1 0 2 -2" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 4 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 4 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-4"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M20 18v-8l-4 6h5" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 5 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 5 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-5"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M17 18h2a2 2 0 1 0 0 -4h-2v-4h4" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 6 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 6 }).run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-h-6"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M19 14a2 2 0 1 0 0 4a2 2 0 0 0 0 -4z" />
          <path d="M21 12a2 2 0 1 0 -4 0v4" />
          <path d="M4 6v12" />
          <path d="M12 6v12" />
          <path d="M11 18h2" />
          <path d="M3 18h2" />
          <path d="M4 12h8" />
          <path d="M3 6h2" />
          <path d="M11 6h2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('bulletList') }"
        @click="editor.chain().focus().toggleBulletList().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-list"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M9 6l11 0" />
          <path d="M9 12l11 0" />
          <path d="M9 18l11 0" />
          <path d="M5 6l0 .01" />
          <path d="M5 12l0 .01" />
          <path d="M5 18l0 .01" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('orderedList') }"
        @click="editor.chain().focus().toggleOrderedList().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-list-numbers"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M11 6h9" />
          <path d="M11 12h9" />
          <path d="M12 18h8" />
          <path d="M4 16a2 2 0 1 1 4 0c0 .591 -.5 1 -1 1.5l-3 2.5h4" />
          <path d="M6 10v-6l-2 2" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('codeBlock') }"
        @click="editor.chain().focus().toggleCodeBlock().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-code"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M7 8l-4 4l4 4" />
          <path d="M17 8l4 4l-4 4" />
          <path d="M14 4l-4 16" />
        </svg>
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('blockquote') }"
        @click="editor.chain().focus().toggleBlockquote().run()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-blockquote"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M6 15h15" />
          <path d="M21 19h-15" />
          <path d="M15 11h6" />
          <path d="M21 7h-6" />
          <path d="M9 9h1a1 1 0 1 1 -1 1v-2.5a2 2 0 0 1 2 -2" />
          <path d="M3 9h1a1 1 0 1 1 -1 1v-2.5a2 2 0 0 1 2 -2" />
        </svg>
      </button>
      <button class="p-1 rounded-sm" @click="editor.chain().focus().setHorizontalRule().run()">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler icons-tabler-outline w-5 h-5 icon-tabler-separator-horizontal"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M4 12l16 0" />
          <path d="M8 8l4 -4l4 4" />
          <path d="M16 16l-4 4l-4 -4" />
        </svg>
      </button>
    </section>
    <EditorContent :editor="editor" />
  </div>
</template>
<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { defineProps, defineModel, defineEmits } from 'vue'

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
  },
  label: {
    type: String,
    default: '',
  },
})

const editor = useEditor({
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  editorProps: {
    attributes: {
      class:
        'border border-gray-200 rounded-sm max-w-none p-2 focus:outline-none min-h-[12rem] max-h-[12rem] overflow-y-auto focus:border-gray-400 prose text-base',
    },
  },
  extensions: [
    StarterKit,
    Underline,
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
  ],
})
</script>
