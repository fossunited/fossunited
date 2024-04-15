<template>
<div v-if="chapter.doc" class="p-8 w-full min-h-screen">
    <div class="flex justify-between">
        <div class="flex flex-col gap-3">
            <FossClubBranding v-if="chapter.doc.chapter_type == 'FOSS Club'">{{ chapter.doc.chapter_type }}</FossClubBranding>
            <CityCommunityBranding v-else>{{ chapter.doc.chapter_type.toUpperCase() }}</CityCommunityBranding>
            <div class="text-3xl font-semibold">{{ chapter.doc.chapter_name }}</div>
        </div>
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
            @click="addNewMember"
        />
    </div>
    <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card v-for="member in chapter.doc.chapter_members" :title="member.full_name">
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
                        }
                    },
                    {
                        label: 'Remove',
                        theme: 'red',
                        onClick: () => {
                            removeMember(selectedMember)
                            showRemoveModal = false
                        }
                    }
                ]
            }"
        >
        </Dialog>
    </div>
</div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, Avatar, Badge, createResource, Dialog } from 'frappe-ui'
import CityCommunityBranding from '@/components/CityCommunityBranding.vue'
import FossClubBranding from '@/components/FossClubBranding.vue'
import { ref } from 'vue'
import { session } from '@/data/session.js'
const route = useRoute();

const chapter = createDocumentResource({
    doctype: 'FOSS Chapter',
    name: `${decodeURI(route.params.id)}`,
    fields: ['*'],
    auto: true,
    transform(doc){
        doc.chapter_members = doc.chapter_members.map(member => {
            return {
                idx: member.idx,
                member: member.chapter_member,
                full_name: member.full_name,
                email: member.email,
                role: member.role,
                profile: getProfile(member.email)
            }
        })
        return doc
    }
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

const addNewMember = () => {
    console.log('Add new member')
}


let showRemoveModal = ref(false)
let selectedMember = ref(null)

const handleRemoveModal = (member) => {
    showRemoveModal.value = true
    selectedMember.value = member
}

const removeMember = (member) => {
    // To Fix: Remove member from chapter.doc.chapter_members
    chapter.setValue.submit({
        chapter_members: chapter.doc.chapter_members.filter(m => m.idx !== member.idx)
    })
}

</script>
