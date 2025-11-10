<template>
  <div class="flex flex-col gap-2">
    <label class="block text-base text-ink-gray-5">
      Session References
      <span class="text-red-500">*</span>
    </label>
    <p class="text-sm text-ink-gray-5">
      Add links to external resources that will help attendees learn more about the session.<br />
      If this is your first talk, please consider submitting a link to one talk recording of yours.
      We may use this to understand your presentation style. A mock presentation may be required if
      this is left empty
    </p>
    <div v-for="(item, index) in references" :key="index" class="flex gap-2 items-center">
      <FormControl
        v-model="item.link"
        type="url"
        variant="outline"
        class="grow"
        placeholder="https://"
      >
        <template #prefix>
          <IconLink size="16" class="text-ink-gray-5" />
        </template>
      </FormControl>
      <Button
        v-if="references.length > 1"
        icon="trash"
        size="sm"
        theme="red"
        @click="deleteReference(index)"
      />
    </div>
    <ErrorMessage :message="errorMessages" />
    <Button size="sm" label="Add another link" icon-left="plus" class="w-fit" @click="addLink" />
  </div>
</template>
<script setup>
import { ErrorMessage, FormControl } from 'frappe-ui'
import { IconLink } from '@tabler/icons-vue'
import { getReferenceItemSchema } from '@/helpers/cfp'
import { ref, watch } from 'vue'

const errorMessages = ref('')

const references = defineModel('references', {
  type: Array,
  required: true,
})

const addLink = () => {
  errorMessages.value = ''
  references.value.push(getReferenceItemSchema())
}

const deleteReference = (index) => {
  if (references.value.length == 1) {
    errorMessages.value = 'Atlease 1 reference is required.'
    setTimeout(() => {
      errorMessages.value = ''
    }, 3000)

    return
  }
  references.value.splice(index, 1)
}
</script>
