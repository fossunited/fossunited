<template>
  <header
    class="sticky top-0 z-50 flex items-center justify-between border-b bg-surface-white px-5 py-2.5"
  >
    <router-link
      to="/"
      aria-label="Go to homepage"
      class="flex gap-1 items-center focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <FossUnitedLogo class="w-auto h-8" fill="black" />
    </router-link>

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
      <a href="/login" class="text-ink-gray-9 font-medium text-base hover:text-ink-gray-8">Login</a>
    </div>
  </header>
</template>
<script setup>
import { inject, computed } from 'vue'
import { Avatar, Dropdown, createResource } from 'frappe-ui'
import FossUnitedLogo from '@/components/FossUnitedLogo.vue'

const session = inject('$session')

const user_profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

if (session.isLoggedIn && session.user != 'Guest' && session.user != 'Administrator') {
  user_profile.fetch()
}

const redirectToProfile = () => {
  window.location.pathname = '/me'
}

const goToPublicSite = () => {
  window.location.pathname = ''
}
</script>
