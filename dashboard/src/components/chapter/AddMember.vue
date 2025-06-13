<template>
  <Dialog
    :options="{
      title: 'Add New Member',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-gray-700">
          Enter the username of the new member you want to add to the team.
        </div>
        <Autocomplete
          v-model="newMembers"
          :options="searchResults"
          placeholder="Search for a user (type at least 2 characters)"
          :multiple="true"
          :loading="isSearching"
          @input-change="handleSearchInput"
          @clear="handleClearSearch"
        >
          <template #item-prefix="{ option }">
            <Avatar
              shape="circle"
              :image="option.avatar"
              :label="option.label"
              size="lg"
            />
          </template>
          <template #empty-state>
            <div class="text-center py-4 text-gray-500">
              <div v-if="searchTerm && searchTerm.length < 2">
                Type at least 2 characters to search
              </div>
              <div
                v-else-if="
                  searchTerm && searchResults.length === 0 && !isSearching
                "
              >
                No users found matching "{{ searchTerm }}"
              </div>
              <div v-else-if="!searchTerm">
                Start typing to search for users
              </div>
            </div>
          </template>
        </Autocomplete>
      </div>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-gray-700">
          Enter the role of the new members you just added
        </div>
        <Select
          v-model="role"
          :options="[
            {
              label: 'Lead',
              value: 'Lead',
            },
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
          :disabled="newMembers.length === 0"
          @click="$emit('update:add-member', newMembers, role)"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import {
  Dialog,
  Autocomplete,
  Select,
  createResource,
  Avatar,
  Button,
} from 'frappe-ui'
import { ref, defineProps, defineEmits, computed, watch } from 'vue'

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
    return props.chapter.doc.chapter_members.map(
      (member) => member.chapter_member,
    )
  }

  if (props.event) {
    return props.event.doc.event_members.map((member) => member.member)
  }

  return []
})

const emits = defineEmits(['update:add-member', 'close-dialog'])

const searchTerm = ref('')
const searchResults = ref([])
const isSearching = ref(false)
let searchTimeout = null

const searchUsers = createResource({
  url: 'fossunited.api.dashboard.search_user_profiles',
  makeParams() {
    return {
      search_term: searchTerm.value,
      existing_members: existingMembers.value,
    }
  },
  transform(data) {
    return data.map((user) => {
      return {
        value: user.name,
        label: user.username,
        description: user.full_name,
        avatar: user.profile_photo
          ? user.profile_photo
          : '/assets/fossunited/images/defaults/user_profile_image.png',
      }
    })
  },
  onSuccess(data) {
    searchResults.value = data
    isSearching.value = false
  },
  onError() {
    searchResults.value = []
    isSearching.value = false
  },
})

const handleSearchInput = (value) => {
  searchTerm.value = value

  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  if (!value || value.length < 2) {
    searchResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true

  searchTimeout = setTimeout(() => {
    searchUsers.fetch()
  }, 300)
}

const handleClearSearch = () => {
  searchTerm.value = ''
  searchResults.value = []
  isSearching.value = false

  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
}

watch(
  existingMembers,
  () => {
    if (searchTerm.value && searchTerm.value.length >= 2) {
      isSearching.value = true
      searchUsers.fetch()
    }
  },
  { deep: true },
)

const newMembers = ref([])
const role = ref('Volunteer')

import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>
