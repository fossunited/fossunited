<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full p-4 md:p-8 border rounded bg-white">
    <h4 v-if="showTitle" class="flex gap-2 items-center font-semibold">
      <IconUserCircle />
      <span>Speaker Information</span>
    </h4>
    <div
      v-for="(speaker, index) in speakers"
      :key="index"
      class="flex flex-col gap-4 p-6 border rounded border-gray-300"
    >
      <div
        v-if="speakers.length > 1"
        class="border-b border-gray-500 pb-2 col-span-2 flex justify-between"
      >
        <h5 class="font-medium text-base">Speaker #{{ index + 1 }}</h5>
        <Button icon="trash" theme="red" @click="deleteSpeaker(index)" />
      </div>
      <FileUploaderArea
        v-model="speaker[getFieldIndex(speaker, 'photo')].value"
        class="col-span-2"
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
        class="col-span-2"
        required="true"
        description="A short bio of the speaker"
      />
    </div>
    <Button label="Add Speaker" icon-left="plus" class="w-fit" @click="addSpeaker" />
  </div>
</template>
<script setup>
import FileUploaderArea from '@/components/ui/FileUploaderArea.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { IconUserCircle } from '@tabler/icons-vue'
import RenderField from '@/components/form/RenderField.vue'
import { getSpeakerFields } from '@/helpers/cfp'

const speakers = defineModel('speakers', {
  type: Array,
  required: true,
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
