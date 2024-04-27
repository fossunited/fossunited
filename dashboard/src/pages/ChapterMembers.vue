<template>
  <div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <div class="flex justify-between mt-4">
      <ChapterHeader :chapter="chapter" />
    </div>
    <div class="flex flex-col mt-4 gap-3 w-fit">
      <div class="text-base text-gray-600">
        Manage team members of your chapter.
      </div>
      <Button
        class="w-fit"
        label="Add New Member"
        icon-left="plus"
        size="md"
        @click="showAddmodal = true"
      />
    </div>
    <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card
        v-for="member in chapter.doc.chapter_members"
        :title="member.full_name"
      >
        <template v-if="member.email != session.user" #actions>
          <Button
            theme="red"
            label="Remove"
            @click="handleRemoveModal(member)"
          />
        </template>
        <div class="flex justify-between">
          <div class="flex flex-col gap-2">
            <div class="text-base text-gray-600">{{ member.email }}</div>
            <Badge
              class="w-fit"
              :label="member.role"
              :theme="member.role === 'Lead' ? 'blue' : 'gray'"
              size="md"
            />
          </div>
        </div>
      </Card>
    </div>
    <div v-if="selectedMember">
      <Dialog
        v-model="showRemoveModal"
        :options="{
          title: 'Remove Team Member?',
          message: `Are you sure you want to remove ${selectedMember.full_name} from the team?`,
          actions: [
            {
              label: 'Cancel',
              theme: 'gray',
              onClick: () => {
                showRemoveModal = false
              },
            },
            {
              label: 'Remove',
              theme: 'red',
              onClick: () => {
                removeMember(selectedMember)
                showRemoveModal = false
              },
            },
          ],
        }"
      >
      </Dialog>
    </div>
    <div v-if="showAddmodal">
      <Dialog
        v-model="showAddmodal"
        :options="{
          title: 'Add New Member',
        }"
      >
        <template #body-content>
          <div class="flex flex-col gap-2">
            <div class="text-p-base text-gray-700">
              Enter the email of the new member you want to add to the team.
            </div>
            <Autocomplete
              :options="allUsers.data"
              v-model="newMembers"
              placeholder="Search for a user"
              :multiple="true"
            />
          </div>
        </template>
        <template #actions>
          <div class="flex gap-3">
            <Button label="Add" theme="green" @click="addNewMember" />
            <Button label="Cancel" theme="gray" @click="showAddmodal = false" />
          </div>
        </template>
      </Dialog>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import {
  createDocumentResource,
  Avatar,
  Select,
  Badge,
  createResource,
  Dialog,
  Autocomplete,
  createListResource,
} from 'frappe-ui'
import ChapterHeader from '@/components/ChapterHeader.vue'
import { ref, watch } from 'vue'
import { session } from '@/data/session.js'
const route = useRoute()

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const getProfile = (email) => {
  const profile = createResource({
    url: 'frappe.client.get',
    params: {
      doctype: 'FOSS User Profile',
      filters: {
        email: email,
      },
    },
    auto: true,
  })
  return profile.data
}

const allUsers = createListResource({
  doctype: 'FOSS User Profile',
  fields: ['*'],
  auto: true,
  realtime: true,
  pageLength: 99999,
  transform(data) {
    return data.map((user) => {
      return {
        value: user.name,
        label: user.full_name,
        description: user.username,
        avatar: user.profile_photo
          ? user.profile_photo
          : '/assets/fossunited/images/defaults/user_profile_image.png',
      }
    })
  },
})
watch(
  () => chapter.doc && chapter.doc.chapter_members,
  (newMembers, oldMembers) => {
    if (newMembers && newMembers !== oldMembers) {
      allUsers.update({
        filters: [
          ['email', 'not in', newMembers.map((m) => m.email).join(',')],
        ],
      })
      allUsers.fetch()
    }
  },
)

let showAddmodal = ref(false)
let newMembers = ref([])
const addNewMember = () => {
  const updatedMembers = chapter.doc.chapter_members.concat(
    newMembers.value.map((value, idx) => {
      return {
        idx: chapter.doc.chapter_members.length + idx + 1,
        chapter_member: value.value,
        role: 'Core Team Member',
      }
    }),
  )
  chapter.setValue.submit({
    chapter_members: updatedMembers,
  })
  showAddmodal.value = false
  newMembers.value = []
}

let showRemoveModal = ref(false)
let selectedMember = ref(null)
const handleRemoveModal = (member) => {
  showRemoveModal.value = true
  selectedMember.value = member
}
const removeMember = (member) => {
  const updatedMembers = chapter.doc.chapter_members.filter(
    (m) => m.idx !== member.idx,
  )
  updatedMembers.forEach((m, idx) => {
    m.idx = idx + 1
  })
  chapter.setValue.submit({
    chapter_members: updatedMembers,
  })
}
</script>
