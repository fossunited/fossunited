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

    <div class="flex items-center gap-2">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-9 transition-colors"
        :title="currentTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
        @click="toggleTheme"
      >
        <IconSun v-if="currentTheme === 'dark'" class="w-5 h-5" />
        <IconMoon v-else class="w-5 h-5" />
      </button>

      <div v-if="session.isLoggedIn">
        <Dropdown
          :options="[
            {
              label: 'My Profile',
              icon: 'user',
              onClick: redirectToProfile,
            },
            {
              label: 'Dashboard',
              icon: 'layout',
              onClick: goToDashboard,
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
            shape="circle"
            class="cursor-pointer"
            :image="
              user_profile.data?.profile_photo ||
              '/assets/fossunited/images/defaults/user_profile_image.png'
            "
            :label="user_profile.data?.full_name?.[0]?.toUpperCase() || '?'"
            size="xl"
          />
        </Dropdown>
      </div>
      <div v-else>
        <a href="/login" class="text-ink-gray-9 font-medium text-base hover:text-ink-gray-8"
          >Login</a
        >
      </div>
    </div>
  </header>
</template>
<script setup>
import { inject } from 'vue'
import { Avatar, Dropdown, createResource, useTheme } from 'frappe-ui'
import { IconSun, IconMoon } from '@tabler/icons-vue'
import FossUnitedLogo from '@/components/FossUnitedLogo.vue'

const session = inject('$session')
const { currentTheme, toggleTheme } = useTheme()

const user_profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

if (session.isLoggedIn && session.user != 'Guest' && session.user != 'Administrator') {
  user_profile.fetch()
}

const redirectToProfile = () => {
  window.location.pathname = '/me'
}

const goToDashboard = () => {
  window.location.pathname = '/dashboard'
}

const goToPublicSite = () => {
  window.location.pathname = ''
}
</script>
