<template>
  <section aria-label="Speaker Information" class="flex flex-col gap-6 w-full p-4 md:p-8 border rounded bg-surface-white">
    <h4 v-if="showTitle" class="flex gap-2 items-center font-semibold">
      <IconUserCircle aria-hidden="true" />
      <span>Speaker Information</span>
    </h4>
    <div :class="speakers.length > 1 ? 'grid md:grid-cols-2 gap-8' : 'flex flex-col gap-8'">
      <div
        v-for="(speaker, index) in speakers"
        :key="index"
        role="group"
        :aria-label="`Speaker ${index + 1}`"
        class="flex flex-col gap-4 p-6 border rounded border-outline-gray-2"
      >
        <div
          v-if="speakers.length > 1"
          class="border-b border-outline-gray-4 pb-2 flex justify-between"
        >
          <h5 class="font-medium text-base">Speaker #{{ index + 1 }}</h5>
          <Button
            icon="trash"
            theme="red"
            :aria-label="`Remove Speaker ${index + 1}`"
            @click="deleteSpeaker(index)"
          />
        </div>
        <FileUploaderArea
          v-model="speaker[getFieldIndex(speaker, 'photo')].value"
          label="Speaker Image"
          description="Please keep the image ratio as 1:1"
          :required="true"
        />
        <RenderField
          v-for="(field, _index) in fields"
          :key="_index"
          v-model:fields="speakers[index]"
          :field="field"
        />
        <TextEditor
          v-model="speaker[getFieldIndex(speaker, 'bio')].value"
          label="Speaker Bio"
          required="true"
          description="A short bio of the speaker"
        />
      </div>
    </div>
    <Button label="Add Speaker" icon-left="plus" class="w-fit" @click="addSpeaker" />

    <div class="flex items-center gap-3 pt-2 border-t border-outline-gray-2">
      <Switch v-model="subscribeNewsletter" />
      <span class="text-sm text-ink-gray-7 leading-relaxed">
        Subscribe to the
        <a
          href="https://fossunited.org/newsletter"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold underline"
          >FOSS United newsletter</a
        >
        for updates on upcoming events and community news.
      </span>
    </div>
  </section>
</template>
<script setup>
import FileUploaderArea from '@/components/ui/FileUploaderArea.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { IconUserCircle } from '@tabler/icons-vue'
import RenderField from '@/components/form/RenderField.vue'
import { getSpeakerFields } from '@/helpers/cfp'
import { Switch } from 'frappe-ui'

const speakers = defineModel('speakers', {
  type: Array,
  required: true,
})

const subscribeNewsletter = defineModel('subscribeNewsletter', {
  type: Boolean,
  default: false,
})

const props = defineProps({
  showTitle: {
    type: Boolean,
    default: true,
  },
})

const fields = getSpeakerFields().filter((field) => !['photo', 'bio'].includes(field.fieldname))

const addSpeaker = () => {
  speakers.value.push(getSpeakerFields())
}

const deleteSpeaker = (index) => {
  speakers.value.splice(index, 1)
}

const getFieldIndex = (speaker, fieldname) => {
  return speaker.findIndex((field) => field.fieldname === fieldname)
}
</script>
