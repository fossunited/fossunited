<template>
  <Dialog
    v-model="showConfimation"
    class="z-50"
    :options="{
      title: 'Remove Showcase?',
      message: `Are you sure you want to remove showcase - ${showcase.showcase_name} ?`,
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'Cancel',
          onClick: () => (showConfimation = false),
        },
        {
          label: 'Remove',
          theme: 'red',
          onClick: handleDelete,
        },
      ],
    }"
  />
  <div class="border p-4 flex flex-col gap-2 rounded items-center">
    <div class="relative w-full">
      <div v-if="editable" class="top-0 right-0 absolute flex flex-row-reverse gap-2 w-full">
        <Button icon="trash" theme="red" @click="showConfimation = true" />
        <Button icon="edit" @click="emit('edit:showcase')" />
      </div>
      <img
        :src="showcase.image"
        class="w-full h-20 px-5 object-contain"
        :alt="label || 'Image preview'"
      />
    </div>
    <h4 class="text-md font-medium">{{ showcase.showcase_name }}</h4>
    <div class="text-sm font-small">{{ showcase.description }}</div>
  </div>
</template>

<script setup>
import { inject, ref } from 'vue'
import { toast } from 'vue-sonner'
import { Dialog } from 'frappe-ui'

const showConfimation = ref(false)
const event = inject('event')

const emit = defineEmits(['edit:showcase', 'reload:event'])

const props = defineProps({
  showcase: {
    type: Object,
    required: true,
  },
  editable: {
    type: Boolean,
    default: () => true,
  },
})

const handleDelete = () => {
  toast.info('Removing showcase...')
  event.setValue
    .submit({
      project_showcase: event.doc.project_showcase.filter(
        (s) => s.name !== props.showcase.name,
      ),
    })
    .then(() => {
      toast.info('Showcase removed successfully')
      emit('reload:event')
      showConfimation.value = false
    })
    .catch((err) => {
      toast.error('Failed to remove showcase' + err)
    })
}
</script>
