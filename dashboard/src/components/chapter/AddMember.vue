<template>
  <Dialog
    :options="{
      title: 'Add New Member',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-ink-gray-6">
          Enter the username of the new member you want to add to the team.
        </div>
        <Autocomplete
          v-model="newMembers"
          :options="memberOptions.data || []"
          placeholder="Search for a user"
          :multiple="true"
          :loading="memberOptions.loading"
          @update:query="handleSearchQuery"
        >
          <template #item-prefix="{ option }">
            <Avatar shape="circle" :image="option.avatar" :label="option.label" size="lg" />
          </template>
        </Autocomplete>
        <div v-if="memberOptions.error" class="text-sm text-ink-red-4">
          Failed to load results. Please try again.
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-ink-gray-6">
          Enter the role of the new members you just added
        </div>
        <Select
          v-model="role"
          :options="[
            {
              label: 'Core Team Member',
              value: 'Core Team Member',
            },
            {
              label: 'Volunteer',
              value: 'Volunteer',
            },
            {
              label: 'Graphic Designer',
              value: 'Graphic Designer',
            },
            {
              label: 'Content Writer',
              value: 'Content Writer',
            },
            {
              label: 'Marketing',
              value: 'Marketing',
            },
          ]"
          :multiple="false"
        >
        </Select>
      </div>
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-3">
        <Button label="Cancel" @click="$emit('close-dialog')" />
        <Button
          label="Add"
          variant="solid"
          :disabled="newMembers.length === 0 || memberOptions.loading"
          @click="$emit('update:add-member', newMembers, role)"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog, Autocomplete, Select, createResource, Avatar, Button } from 'frappe-ui'
import { ref, defineProps, defineEmits, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  chapter: {
    type: Object,
    default: () => null,
  },
  event: {
    type: Object,
    default: () => null,
  },
})

const existingMembers = computed(() => {
  if (props.chapter) {
    return props.chapter.doc.chapter_members.map((member) => member.chapter_member)
  }
  if (props.event) {
    return props.event.doc.event_members.map((member) => member.member)
  }
  return []
})

const emits = defineEmits(['update:add-member', 'close-dialog'])

const searchTerm = ref('')
const MIN_QUERY_CHARS = 2

const memberOptions = createResource({
  url: 'fossunited.api.dashboard.get_user_profile_list',
  makeParams() {
    const params = {
      filters: { name: ['not in', existingMembers.value] },
    }
    if (searchTerm.value?.trim().length >= MIN_QUERY_CHARS) {
      params.search_term = searchTerm.value.trim()
    }
    return params
  },
  transform(data) {
    return data.map((user) => {
      return {
        value: user.name,
        label: user.full_name ? `${user.full_name} (${user.username})` : user.username,
        description: user.full_name || user.username,
        avatar: user.profile_photo
          ? user.profile_photo
          : '/assets/fossunited/images/defaults/user_profile_image.png',
      }
    })
  },
})

let searchTimeout = null
const handleSearchQuery = (query) => {
  searchTerm.value = (query || '').trim()

  if (searchTimeout) clearTimeout(searchTimeout)

  if (searchTerm.value.length < MIN_QUERY_CHARS) {
    return
  }

  searchTimeout = setTimeout(() => {
    memberOptions.fetch()
  }, 300)
}

watch(
  existingMembers,
  () => {
    if (searchTerm.value.trim().length >= MIN_QUERY_CHARS) {
      memberOptions.fetch()
    }
  },
  { deep: false },
)

const newMembers = ref([])
const role = ref('Volunteer')

onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>
