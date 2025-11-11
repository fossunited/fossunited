<script setup>
import { IconCircleCheckFilled } from '@tabler/icons-vue'
import { Badge, FormControl, Dialog, ErrorMessage } from 'frappe-ui'
import { computed, inject, ref, onMounted, onUnmounted } from 'vue'
import { toast } from 'vue-sonner'

const event = inject('event')
const emit = defineEmits(['update:schedule', 'delete:schedule'])
const selectedScheduleItem = defineModel({ type: Object, required: true })

const SCHEDULE_CATEGORIES = [
  'Talk',
  'Lightning Talk',
  'Workshop',
  'Panel Discussion',
  'Opening Note',
  'Break',
  'Other',
]

const CATEGORIES_WITHOUT_CFP = ['Opening Note', 'Break']
const CATEGORIES_REQUIRING_CFP = ['Lightning Talk', 'Workshop', 'Panel Discussion']

const allCfpSubmissions = inject('allCfpSubmissions')
const linkedCfpSubmissions = inject('linkedCfpSubmissions')

// Computed properties
const getLinkedCfpOptions = computed(() => {
  return allCfpSubmissions.data
    .filter(
      (cfp) =>
        !linkedCfpSubmissions.value.includes(cfp.name) ||
        cfp.name === selectedScheduleItem.value.linked_cfp,
    )
    .map((cfp) => ({
      label: cfp.talk_title,
      value: cfp.name,
    }))
})

const getHallOptions = computed(() => {
  if (!event.doc.hall_options) return ['']

  const options = event.doc.hall_options
    .split('\n')
    .map((option) => option.trim())
    .filter(Boolean)

  return ['', ...options]
})

const showCfpField = computed(
  () => !CATEGORIES_WITHOUT_CFP.includes(selectedScheduleItem.value.category),
)

// Handle CFP selection
const handleCfpChange = (cfpName) => {
  if (CATEGORIES_WITHOUT_CFP.includes(selectedScheduleItem.value.category)) {
    return
  }

  if (!cfpName) {
    selectedScheduleItem.value.title = ''
    selectedScheduleItem.value.category = ''
    selectedScheduleItem.value.talk_video = ''
    return
  }

  const cfpValue = typeof cfpName === 'object' ? cfpName.value : cfpName
  const cfp = allCfpSubmissions.data.find((c) => c.name === cfpValue)

  if (cfp) {
    // Update the linked_cfp value properly
    selectedScheduleItem.value.linked_cfp = cfpValue
    selectedScheduleItem.value.title = cfp.talk_title
    selectedScheduleItem.value.category = cfp.session_type
    // Only set talk_video if it exists and current value is empty
    if (cfp.talk_video && !selectedScheduleItem.value.talk_video) {
      selectedScheduleItem.value.talk_video = cfp.talk_video
    }
  }
}

// Validation
const errorMessages = ref('')

const validateScheduleItem = () => {
  const errors = []
  const item = selectedScheduleItem.value

  if (!item.title) errors.push('Title is required')
  if (!item.category) errors.push('Category is required')
  if (!item.hall) errors.push('Hall is required')
  if (!item.scheduled_date) errors.push('Date is required')
  if (!item.start_time) errors.push('Start Time is required')
  if (!item.end_time) errors.push('End Time is required')

  // Clear linked_cfp for categories that don't need it
  if (CATEGORIES_WITHOUT_CFP.includes(item.category)) {
    item.linked_cfp = ''
  }

  // Require linked_cfp for specific categories
  if (CATEGORIES_REQUIRING_CFP.includes(item.category) && !item.linked_cfp) {
    errors.push('Linked Proposal is required')
  }

  // Validate time order
  if (item.start_time && item.end_time) {
    const [startHour, startMin] = item.start_time.split(':').map(Number)
    const [endHour, endMin] = item.end_time.split(':').map(Number)

    if (endHour < startHour || (endHour === startHour && endMin <= startMin)) {
      errors.push('End Time must be after Start Time')
    }
  }

  return errors
}

// Actions
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

const handleDelete = () => {
  emit('delete:schedule', selectedScheduleItem.value)
  showDeleteConfirmation.value = false
}

const showDeleteConfirmation = ref(false)

// Keyboard shortcut
const saveShortcut = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    handleSave()
  }
}

onMounted(() => window.addEventListener('keydown', saveShortcut))
onUnmounted(() => window.removeEventListener('keydown', saveShortcut))
</script>

<template>
  <Dialog
    v-model="showDeleteConfirmation"
    class="z-50"
    :options="{
      title: 'Delete Schedule',
      message: 'Are you sure you want to delete this schedule? This action cannot be undone.',
      icon: { name: 'trash', appearance: 'danger' },
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
          onClick: () => (showDeleteConfirmation = false),
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
        <!-- Linked Proposal (CFP) -->
        <FormControl
          v-if="showCfpField"
          :model-value="selectedScheduleItem.linked_cfp"
          label="Linked Proposal"
          type="autocomplete"
          variant="outline"
          description="Choose a proposal from approved submissions"
          :options="getLinkedCfpOptions"
          @update:model-value="
            (value) => {
              selectedScheduleItem.linked_cfp = value
              handleCfpChange(value)
            }
          "
        >
          <template #item-prefix="{ selected }">
            <div class="flex gap-2 items-center">
              <IconCircleCheckFilled v-if="selected" class="w-4 h-4" />
              <Badge :label="selectedScheduleItem.category" />
            </div>
          </template>
        </FormControl>

        <!-- Category -->
        <FormControl
          v-model="selectedScheduleItem.category"
          label="Category"
          type="select"
          variant="outline"
          :options="SCHEDULE_CATEGORIES"
          required
        />

        <!-- Other Category (conditional) -->
        <FormControl
          v-if="selectedScheduleItem.category === 'Other'"
          v-model="selectedScheduleItem.other_category"
          label="Other Category"
          variant="outline"
          required
        />

        <!-- Title -->
        <FormControl
          v-model="selectedScheduleItem.title"
          label="Title"
          variant="outline"
          required
        />

        <!-- Hall -->
        <FormControl
          v-model="selectedScheduleItem.hall"
          label="Hall"
          type="select"
          variant="outline"
          :options="getHallOptions"
          required
        />

        <!-- Date and Time -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-2">
          <FormControl
            v-model="selectedScheduleItem.scheduled_date"
            label="Date"
            type="date"
            variant="outline"
          />
          <FormControl
            v-model="selectedScheduleItem.start_time"
            label="Start Time"
            type="time"
            variant="outline"
          />
          <FormControl
            v-model="selectedScheduleItem.end_time"
            label="End Time"
            type="time"
            variant="outline"
          />
        </div>

        <!-- Talk Video -->
        <FormControl
          v-model="selectedScheduleItem.talk_video"
          label="Talk Video Link"
          type="text"
          variant="outline"
        />
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col gap-4">
      <ErrorMessage v-if="errorMessages" class="mt-2" :message="errorMessages" />

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
