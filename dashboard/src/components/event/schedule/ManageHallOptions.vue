<script setup>
import { IconHomeFilled, IconX } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import { computed, ref, watch, inject } from 'vue'
const hall_options = defineModel({ type: String, default: '' })

const event = inject('event')

const hall_options_list = computed({
  get() {
    if (!hall_options.value) {
      return []
    }

    return hall_options.value.split('\n').map((option) => option.trim())
  },

  set(newValue) {
    hall_options.value = newValue.join('\n')
  },
})

const new_option = ref('')
watch(
  () => new_option.value,
  () => {
    if (new_option.value.endsWith('\n')) {
      const trimmedOption = new_option.value.trim()
      if (trimmedOption && !hall_options_list.value.includes(trimmedOption)) {
        hall_options_list.value = [...hall_options_list.value, trimmedOption]
      }
      new_option.value = ''
      addHallOption()
    }
  },
)

const handleDeleteHall = (option) => {
  hall_options_list.value = hall_options_list.value.filter((o) => o !== option)
  addHallOption()
}

const addHallOption = () => {
  event.setValue.submit({ hall_options: event.doc.hall_options })
  toast.info('Hall Options Updated')
}
</script>
<template>
  <div class="flex flex-col gap-2 mt-4">
    <div class="flex gap-2 items-center">
      <IconHomeFilled class="w-4 h-4" />
      <span class="text-sm font-semibold">Hall Options</span>
    </div>
    <div class="flex flex-col gap-2 p-2 bg-surface-white border rounded-sm">
      <div class="flex gap-2 flex-wrap">
        <div
          v-for="option in hall_options_list"
          :key="option"
          class="flex items-center gap-2 text-sm border p-1 rounded-xs bg-surface-gray-1"
        >
          {{ option }}
          <button @click.prevent="handleDeleteHall(option)"><IconX class="w-3 h-3" /></button>
        </div>
      </div>
      <textarea
        placeholder="Add a new option"
        v-model="new_option"
        class="border-0 text-sm focus:!outline-none focus:ring-0 focus-visible:outline-none resize-none"
      ></textarea>
    </div>
    <small class="text-ink-gray-5">Separate each option with a new line</small>
  </div>
</template>
