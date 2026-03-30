<template>
  <Dialog
    v-model="showConfirmation"
    class="z-50"
    :options="{
      title: `Remove ${label}?`,
      message: `Are you sure you want to remove ${label.toLowerCase()} - ${item[nameKey]}?`,
      icon: { name: 'alert-triangle', appearance: 'warning' },
      actions: [
        { label: 'Cancel', onClick: () => (showConfirmation = false) },
        { label: 'Remove', theme: 'red', onClick: handleDelete },
      ],
    }"
  />
  <div class="border p-4 flex flex-col gap-2 rounded items-center">
    <div class="relative w-full">
      <div v-if="editable" class="top-0 right-0 absolute flex flex-row-reverse gap-2 z-10">
        <Button icon="trash" theme="red" @click="showConfirmation = true" />
        <Button icon="edit" @click="emit('edit')" />
      </div>
      <img
        :src="item[imageKey]"
        class="w-auto mx-auto h-20 px-5 object-contain"
        :alt="item[nameKey] || 'Image preview'"
      />
    </div>
    <h4 class="text-md font-medium">{{ item[nameKey] }}</h4>
    <slot />
  </div>
</template>

<script setup>
import { inject, ref } from 'vue'
import { toast } from 'vue-sonner'
import { Dialog } from 'frappe-ui'

const props = defineProps({
  item: { type: Object, required: true },
  imageKey: { type: String, required: true },
  nameKey: { type: String, required: true },
  eventField: { type: String, required: true },
  label: { type: String, required: true },
  editable: { type: Boolean, default: true },
})

const emit = defineEmits(['edit', 'reload:event'])

const showConfirmation = ref(false)
const event = inject('event')

const handleDelete = () => {
  toast.info(`Removing ${props.label.toLowerCase()}...`)
  event.setValue
    .submit({
      [props.eventField]: event.doc[props.eventField].filter((s) => s.name !== props.item.name),
    })
    .then(() => {
      toast.info(`${props.label} removed successfully`)
      emit('reload:event')
      showConfirmation.value = false
    })
    .catch((err) => {
      toast.error(`Failed to remove ${props.label.toLowerCase()}: ` + err)
    })
}
</script>
