<template>
  <header
    class="sticky top-0 z-40 flex items-center justify-between border-b bg-white px-5 py-2"
  >
    <div>
      <button class="block md:hidden" @click="handleToggleSidebar()">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler w-5 h-5 icons-tabler-outline icon-tabler-menu-2"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M4 6l16 0" />
          <path d="M4 12l16 0" />
          <path d="M4 18l16 0" />
        </svg>
      </button>
    </div>
    <div v-if="session.isLoggedIn" class="flex items-center">
      <Dropdown
        :options="[
          {
            label: 'My Profile',
            icon: 'user',
            onClick: redirectToProfile,
          },
          {
            label: 'Go to website',
            icon: 'globe',
            onClick: goToPublicSite,
          },
          {
            label: 'Logout',
            icon: 'log-out',
            onClick: () => {
              session.logout.fetch()
            },
          },
        ]"
      >
        <Avatar
          v-if="user_profile.data"
          :shape="'circle'"
          class="cursor-pointer"
          :image="
            user_profile.data.profile_photo ||
            '/assets/fossunited/images/defaults/user_profile_image.png'
          "
          :label="user_profile.data.full_name[0].toUpperCase()"
          size="xl"
        />
      </Dropdown>
    </div>
    <div v-else>
      <a
        href="/login"
        class="text-black font-medium text-base hover:text-gray-800"
        >Login</a
      >
    </div>
    <div v-if="showNav" class="block md:hidden fixed inset-0 bg-black opacity-20 z-30 mt-[55px]" @click="handleToggleSidebar"></div>
  </header>
</template>
<script setup>
import { inject, ref, defineEmits } from 'vue'
import { Avatar, Dropdown, createResource } from 'frappe-ui'

let session = inject('$session')

let showNav = ref(false)

const emit = defineEmits(['toggleSidebar'])

const handleToggleSidebar = () => {
  showNav.value = !showNav.value
  emit('toggleSidebar', showNav.value)
}

let user_profile = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS User Profile',
    filters: {
      email: session.user,
    },
  },
})

if (
  session.isLoggedIn &&
  session.user != 'Guest' &&
  session.user != 'Administrator'
) {
  user_profile.fetch()
}

const redirectToProfile = () => {
  window.location.pathname = '/me'
}

const goToPublicSite = () => {
  window.location.pathname = ''
}
</script>
