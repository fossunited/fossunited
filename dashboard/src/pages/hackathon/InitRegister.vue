<template>
  <Header />
  <div
    class="w-full p-4 flex justify-center items-center"
    v-if="hackathon.data && !team.loading"
  >
    <div class="w-full max-w-screen-xl">
      <div class="flex gap-2 my-6 items-center text-base uppercase">
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
        <span>{{ hackathon.data.hackathon_name }}</span>
      </div>
      <HackathonHeader :hackathon="hackathon" />
      <hr class="my-6" />
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2 pt-6 md:p-0">
        <div
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center md:border-r-2"
        >
          <div
            class="px-4 py-2 w-3/4 text-center uppercase border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
            @click="$router.push(`/hack/${hackathonPermalink}/create-team`)"
          >
            Create team
          </div>
          <p class="text-base text-center leading-normal">
            Create a team and invite your friends to join you in the hackathon.
            <br />If you are hacking alone, create a team with only yourself.
          </p>
        </div>
        <div class="md:hidden w-full text-center font-medium">OR</div>
        <div
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center"
        >
          <div
            class="px-4 py-2 uppercase w-3/4 text-center border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
          >
            Join team
          </div>
          <p class="text-base text-center leading-normal">
            Join existing teams looking for members.
          </p>
        </div>
      </div>
      <RouterView />
    </div>
  </div>
  <div v-else class="w-full h-screen flex justify-center align-middle">
    <LoadingIndicator class="w-8" />
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const session = inject('$session')
const route = useRoute()
const router = useRouter()

const hackathonPermalink = route.params.permalink

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: hackathonPermalink,
  },
  auto: true,
  onSuccess(data) {
    team.update({
      params: {
        doctype: 'FOSS Hackathon Team',
        filters: [
          ['hackathon', '=', data.name],
          ['FOSS Hackathon Team Member', 'email', '=', session.user],
        ],
      },
    })
    team.fetch()
  },
})

const team = createResource({
  url: 'frappe.client.get_count',
  onSuccess(data) {
    if (data > 0) {
      router.push({
        name: 'MyHackathonTeam',
      })
    }
  },
  loading: true,
})
</script>
