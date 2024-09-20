<template>
  <div
    v-if="chapter.doc"
    class="px-4 py-8 md:p-8 w-full z-0 min-h-screen"
    :class="chapter.get.loading ? 'animate-pulse' : ''"
  >
    <div class="flex justify-between mt-4">
      <ChapterHeader :chapter="chapter" />
    </div>
    <div class="flex flex-col mt-4 gap-3 w-fit">
      <div class="text-base text-gray-600">Manage team members of your chapter.</div>
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
        :key="member.name"
        :title="member.full_name"
      >
        <template v-if="member.email != session.user && member.role != 'Lead'" #actions>
          <Button theme="red" label="Remove" @click="handleRemoveModal(member)" />
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

    <!-- REMOVE A MEMBER -->
    <div v-if="selectedMember">
      <Dialog
        v-model="showRemoveModal"
        class="z-50"
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

    <!-- ADD NEW MEMBER -->
    <div v-if="showAddmodal">
      <AddMemberDialog
        v-model="showAddmodal"
        class="z-50"
        :chapter="chapter"
        @update:add-member="addNewMember"
        @close-dialog="showAddmodal = false"
      />
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, Badge, Dialog } from 'frappe-ui'
import { ref, inject } from 'vue'
import AddMemberDialog from '@/components/chapter/AddMember.vue'
import ChapterHeader from '@/components/ChapterHeader.vue'

const session = inject('$session')
const route = useRoute()

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const showAddmodal = ref(false)

const addNewMember = (newMembers) => {
  showAddmodal.value = false
  const updatedMembers = chapter.doc.chapter_members.concat(
    newMembers.map((value, idx) => {
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
}

const showRemoveModal = ref(false)
const selectedMember = ref(null)

const handleRemoveModal = (member) => {
  showRemoveModal.value = true
  selectedMember.value = member
}

const removeMember = (member) => {
  let updatedMembers = chapter.doc.chapter_members.filter((m) => m.idx !== member.idx)
  updatedMembers.forEach((m, idx) => {
    m.idx = idx + 1
  })
  chapter.setValue.submit({
    chapter_members: updatedMembers,
  })
}
</script>
