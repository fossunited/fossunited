<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <EventHeader :event="event.doc" />

    <div class="flex flex-col mt-4 gap-3 w-fit">
      <div class="text-base text-gray-600">Manage volunteers of the event.</div>
      <Button
        class="w-fit"
        label="Add Volunteer"
        icon-left="plus"
        size="md"
        @click="showAddmodal = true"
      />
    </div>

    <!-- VOLUNTEERS GRID -->
    <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card v-for="member in event.doc.event_members" :key="member.name" :title="member.full_name">
        <template v-if="member.email != session.user" #actions>
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

    <div v-if="showAddmodal">
      <AddMemberDialog
        v-model="showAddmodal"
        class="z-50"
        :event="event"
        @update:add-member="addNewMember"
        @close-dialog="showAddmodal = false"
      />
    </div>
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import AddMemberDialog from '@/components/chapter/AddMember.vue'
import { createDocumentResource, Badge, Dialog } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, inject } from 'vue'
const session = inject('$session')

const route = useRoute()

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const showAddmodal = ref(false)

const addNewMember = (newMembers) => {
  const updatedMembers = event.doc.event_members.concat(
    newMembers.map((value, idx) => {
      return {
        idx: event.doc.event_members.length + idx + 1,
        member: value.value,
        role: 'Volunteer',
      }
    }),
  )
  event.setValue.submit({
    event_members: updatedMembers,
  })
  showAddmodal.value = false
}

const showRemoveModal = ref(false)
const selectedMember = ref(null)

const handleRemoveModal = (member) => {
  showRemoveModal.value = true
  selectedMember.value = member
}
const removeMember = (member) => {
  const updatedMembers = event.doc.event_members.filter((m) => m.idx !== member.idx)
  updatedMembers.forEach((m, idx) => {
    m.idx = idx + 1
  })
  event.setValue.submit({
    event_members: updatedMembers,
  })
}
</script>
