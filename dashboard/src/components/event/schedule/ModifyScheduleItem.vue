<script setup>
import { IconCircleCheckFilled } from '@tabler/icons-vue'
import { Badge, FormControl, Dialog, ErrorMessage } from 'frappe-ui'
import { computed, inject, watch, onMounted, ref, onUnmounted } from 'vue'
import { toast } from 'vue-sonner'

const event = inject('event')
const emit = defineEmits(['update:schedule', 'delete:schedule'])

const selectedScheduleItem = defineModel({ type: Object, required: true })

const scheduleCategories = [
  'Talk',
  'Lightning Talk',
  'Workshop',
  'Panel Discussion',
  'Opening Note',
  'Break',
  'Other',
]

const allCfpSubmissions = inject('allCfpSubmissions')
const linkedCfpSubmissions = inject('linkedCfpSubmissions')

const getLinkedCfpOptions = computed(() => {
  return allCfpSubmissions.data
    .filter(
      (cfp) =>
        !linkedCfpSubmissions.value.includes(cfp.name) ||
        cfp.name === selectedScheduleItem.value.linked_cfp,
    )
    .map((cfp) => {
      return {
        label: cfp.talk_title,
        value: cfp.name,
      }
    })
})

watch(
  () => selectedScheduleItem.value.linked_cfp,
  (newValue) => {
    if (
      selectedScheduleItem.value.category === 'Opening Note' ||
      selectedScheduleItem.value.category === 'Break'
    ) {
      return
    }

    if (!newValue) {
      selectedScheduleItem.value.title = ''
      selectedScheduleItem.value.category = ''
      return
    }

    if (typeof newValue == 'object') {
      newValue = newValue.value
    }

    const target = allCfpSubmissions.data.find((cfp) => cfp.name === newValue)

    selectedScheduleItem.value.title = target.talk_title
    selectedScheduleItem.value.category = target.session_type
  },
)

const errorMessages = ref('')
const handleSave = () => {
  const errors = validateScheduleItem()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  errorMessages.value = ''

  emit('update:schedule', selectedScheduleItem.value)
  toast.info('Schedule updated')
}

watch(
  () => selectedScheduleItem.value,
  () => {
    errorMessages.value = ''
  },
)

const validateScheduleItem = () => {
  const errors = []
  if (!selectedScheduleItem.value.title) {
    errors.push('Title is required')
  }

  if (!selectedScheduleItem.value.category) {
    errors.push('Category is required')
  }

  if (
    selectedScheduleItem.value.category === 'Opening Note' ||
    selectedScheduleItem.value.category === 'Break'
  ) {
    selectedScheduleItem.value.linked_cfp = ''
  }

  if (!['Talk', 'Other', 'Opening Note', 'Break'].includes(selectedScheduleItem.value.category)) {
    if (!selectedScheduleItem.value.linked_cfp) {
      errors.push('Linked Proposal is required')
    }
  }

  if (!selectedScheduleItem.value.hall) {
    errors.push('Hall value is required')
  }

  if (!selectedScheduleItem.value.scheduled_date) {
    errors.push('Date is required')
  }

  if (!selectedScheduleItem.value.start_time) {
    errors.push('Start Time is required')
  }

  if (!selectedScheduleItem.value.end_time) {
    errors.push('End Time is required')
  }

  // Validate that end time is not before start time
  if (selectedScheduleItem.value.start_time && selectedScheduleItem.value.end_time) {
    // Compare as "HH:mm"
    const [startHour, startMinute] = selectedScheduleItem.value.start_time.split(':').map(Number)
    const [endHour, endMinute] = selectedScheduleItem.value.end_time.split(':').map(Number)
    if (endHour < startHour || (endHour === startHour && endMinute < startMinute)) {
      errors.push('End Time cannot be before Start Time')
    }
  }

  return errors
}

const showDeleteConfirmation = ref(false)

const saveShortcut = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key == 's') {
    e.preventDefault()
    handleSave()
  }
}

onMounted(() => {
  window.addEventListener('keydown', saveShortcut)
})

onUnmounted(() => {
  window.removeEventListener('keydown', saveShortcut)
})

const getHallOptions = computed(() => {
  if (!event.doc.hall_options) {
    return []
  }

  let options = event.doc.hall_options.split('\n').map((option) => option.trim())
  options.unshift('')

  return options
})
</script>
<template>
  <Dialog
    v-model="showDeleteConfirmation"
    class="z-50"
    :options="{
      title: 'Delete Schedule',
      message: `Are you sure you want to delete this schedule? This action cannot be undone.`,
      icon: {
        name: 'trash',
        appearance: 'danger',
      },
      actions: [
        {
          label: 'Delete',
          theme: 'red',
          onClick: () => {
            emit('delete:schedule', selectedScheduleItem)
            showDeleteConfirmation = false
          },
        },
        {
          label: 'Cancel',
          onClick: () => (showDeleteConfirmation.value = false),
        },
      ],
    }"
  />
  <div class="flex flex-col gap-2 justify-between h-full">
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h3>Modify Schedule</h3>
      </div>
      <div class="my-2 flex flex-col gap-4">
        <FormControl
          v-if="
            selectedScheduleItem.category !== 'Opening Note' &&
            selectedScheduleItem.category !== 'Break'
          "
          v-model="selectedScheduleItem.linked_cfp"
          label="Linked Proposal"
          type="autocomplete"
          variant="outline"
          description="Choose a proposal from the following list of approved proposals"
          :options="getLinkedCfpOptions"
        >
          <template #item-prefix="{ selected }">
            <div class="flex gap-2 items-center">
              <IconCircleCheckFilled v-if="selected" class="w-4 h-4" />
              <Badge :label="selectedScheduleItem.category" />
            </div>
          </template>
        </FormControl>
        <FormControl
          v-model="selectedScheduleItem.category"
          label="Category"
          :options="scheduleCategories"
          type="select"
          variant="outline"
          required
        />
        <FormControl
          v-if="selectedScheduleItem.category === 'Other'"
          v-model="selectedScheduleItem.other_category"
          label="Other Category"
          variant="outline"
          required
        />
        <FormControl
          v-model="selectedScheduleItem.title"
          label="Title"
          variant="outline"
          required
        />
        <FormControl
          v-model="selectedScheduleItem.hall"
          label="Hall"
          variant="outline"
          type="select"
          :options="getHallOptions"
          required
        />
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-2">
          <FormControl
            v-model="selectedScheduleItem.scheduled_date"
            variant="outline"
            label="Date"
            type="date"
          />
          <FormControl
            v-model="selectedScheduleItem.start_time"
            variant="outline"
            label="Start Time"
            type="time"
          />
          <FormControl
            v-model="selectedScheduleItem.end_time"
            variant="outline"
            label="End Time"
            type="time"
          />
        </div>
      </div>
    </div>
    <div class="flex flex-col gap-4">
      <ErrorMessage class="mt-2" :message="errorMessages" />
      <div class="bg-white flex gap-2 items-center">
        <Button
          icon="trash"
          theme="red"
          class="basis-1/6"
          @click="showDeleteConfirmation = true"
        />
        <Button label="Save" variant="solid" class="basis-5/6" @click="handleSave">
          <template #suffix>
            <span
              class="px-[2px] pt-[4px] hidden md:block font-mono rounded-[2px] border text-[10px] opacity-80"
            >
              ctrl + s
            </span>
          </template>
        </Button>
      </div>
    </div>
  </div>
</template>
