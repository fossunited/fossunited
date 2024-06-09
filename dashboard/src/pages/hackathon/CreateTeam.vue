<template>
  <Header />
  <div
    class="w-full p-4 flex justify-center items-center"
    v-if="hackathon.data"
  >
    <div class="w-full max-w-screen-xl">
      <div class="flex flex-wrap gap-2 my-6 items-center text-base uppercase">
        <span class="font-semibold">My Hackathons</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="m8.25 4.5 7.5 7.5-7.5 7.5"
          />
        </svg>
        <span class="font-semibold">{{ hackathon.data.hackathon_name }}</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="m8.25 4.5 7.5 7.5-7.5 7.5"
          />
        </svg>
        <span>Create Team</span>
      </div>
      <HackathonHeader v-if="hackathon.data" :hackathon="hackathon" />
      <hr class="my-6" />
      <div>
        <div class="prose mt-5 mb-3">
            <h3>Create Team</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormControl type="text" label="Team Name" v-model="team.team_name" />
          <div></div>
          <FormControl type="checkbox" label="Looking for team members" v-model="team.looking_for_members" />
        </div>
      </div>
      <div class="flex flex-col p-4 w-full rounded-sm my-4 border-2 bg-gray-100 border-gray-800 border-dashed text-gray-800">
        <div class="text-base font-semibold mb-2">Team Members</div>
        <p class="text-sm">You can add members after team creation</p>
      </div>
      <ErrorMessage v-if="errorMessage" :message="errorMessage" />
      <div class="mt-8 grid grid-cols-1 md:grid-cols-2">
        <div class="hidden md:block"></div>
        <Button
            variant="solid"
            theme="green"
            size="md"
            label="Create"
            class="font-semibold"
            :loading="createTeam.loading"
            @click="handleTeamCreation"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import { createResource, FormControl, ErrorMessage } from 'frappe-ui'
import { reactive, inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const session = inject('$session')

const team = reactive({
  team_name: '',
  hackathon: '',
  looking_for_members: false,
  members: [],
})

const userParticipantInfo = createResource({
    url: 'fossunited.api.hackathon.get_participant',
    onSuccess(data){
        team.members.push({
            member: data.name
        })
    },
    onError(error){
        console.log(error)
    }
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: route.params.permalink,
  },
  auto: true,
  onSuccess: (data) => {
    team.hackathon = data.name
    userParticipantInfo.update({
        params: {
            hackathon: data.name,
            user: session.user,
        }
    })
    userParticipantInfo.fetch()
  }
})

const validateFields = () => {
    const errors = []
    if ( team.team_name === '' ) {
        errors.push('Team Name is required')
    }
    return errors
}

let errorMessage = ref('')

const createTeam = createResource({
    url: 'fossunited.api.hackathon.create_team',
    onSuccess(data){
        router.push({
          name: 'MyHackathonTeam'
        })
    },
    onError(error){
        console.log(error)
    }
})

const handleTeamCreation = () => {
    if (validateFields().length > 0) {
        errorMessage.value = validateFields().join(', ')
        return
    }
    else{
      errorMessage.value = ''
    }
    createTeam.update({
        params: {
            hackathon: hackathon.data.name,
            team: team,
        }
    })
    createTeam.fetch()
}

</script>
