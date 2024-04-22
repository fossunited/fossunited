<template>

    <header
    class="sticky top-0 z-50 flex items-center justify-between border-b bg-white px-5 py-2.5"
    >
    <div class="flex gap-1">
    <FossUnitedLogo class="w-auto h-8" fill="black"></FossUnitedLogo>
    </div>
    <div class="flex items-center">
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
        <div class="flex items-center gap-1">
          <img
            v-if="user_profile.data"
            class="w-8 h-8 rounded-full text-xs"
            :src="user_profile.data.profile_photo || '/assets/fossunited/images/defaults/user_profile_image.png'"
            :alt="user_profile.data.full_name"
          />
        </div>
    </Dropdown>
    </div>
    </header>
</template>
<script setup>
import { session } from '@/data/session.js'
import { Dropdown, createResource } from 'frappe-ui';
import FossUnitedLogo from '@/components/FossUnitedLogo.vue'

let user_profile = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS User Profile',
    filters: {
      email: session.user,
    }
  },
  auto: true,
  cache: 'user',
})

const redirectToProfile = () => {
  window.location.pathname = '/me'
}

const goToPublicSite = () => {
  window.location.pathname = ''
}
</script>
