<template>
  <header
    class="z-50 flex items-center justify-between border-b bg-surface-white dark:bg-surface-gray-1 px-4 sm:px-5 py-2.5 transition-colors"
    :class="{ 'sticky top-0': sticky }"
  >
    <!-- Brand & Navigation -->
    <div class="flex items-center gap-4 lg:gap-6">
      <template v-if="isIndiaFoss">
        <a
          :href="`/indiafoss/${currentYear}`"
          aria-label="IndiaFOSS home"
          class="flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
        >
          <IndiaFossLogo />
        </a>

        <!-- Desktop Navigation Tabs -->
        <nav class="hidden md:flex items-center gap-1" aria-label="IndiaFOSS navigation">
          <a
            v-for="link in navLinks"
            :key="link.id"
            :href="link.url"
            class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-bold tracking-wider uppercase transition-colors"
            :class="
              activeTab === link.id
                ? 'bg-surface-gray-3 dark:bg-surface-gray-3 text-ink-gray-9 dark:text-ink-gray-1'
                : 'text-ink-gray-7 dark:text-ink-gray-8 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3 hover:text-ink-gray-9 dark:hover:text-ink-gray-1'
            "
            :aria-current="activeTab === link.id ? 'page' : undefined"
          >
            {{ link.label }}
          </a>
        </nav>
      </template>

      <router-link
        v-else
        to="/"
        aria-label="Go to homepage"
        class="flex gap-1 items-center focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <FossUnitedLogo class="w-auto h-8" fill="black" />
      </router-link>
    </div>

    <!-- Right Controls -->
    <div class="flex items-center gap-2 sm:gap-3">
      <span
        v-if="isIndiaFoss"
        class="hidden xl:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider text-ink-gray-6 dark:text-ink-gray-7 bg-surface-gray-2 dark:bg-surface-gray-3 border border-outline-gray-3"
      >
        IndiaFOSS {{ currentYear }}
      </span>

      <ThemeToggle :size="20" />
      <div v-if="session.isLoggedIn" class="flex items-center">
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

      <!-- Mobile Menu Toggle Button for IndiaFOSS -->
      <button
        v-if="isIndiaFoss"
        type="button"
        id="indiafoss-mobile-menu-btn"
        class="md:hidden flex items-center justify-center p-1.5 rounded border border-outline-gray-3 bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-7 dark:text-ink-gray-8 hover:text-ink-gray-9 dark:hover:text-ink-gray-1"
        :aria-label="mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'"
        :aria-expanded="mobileMenuOpen"
        aria-controls="indiafoss-mobile-menu"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <IconMenu2 v-if="!mobileMenuOpen" class="w-5 h-5" />
        <IconX v-else class="w-5 h-5" />
      </button>
    </div>
  </header>

  <!-- Mobile Collapsible Menu for IndiaFOSS -->
  <div
    v-if="isIndiaFoss && mobileMenuOpen"
    id="indiafoss-mobile-menu"
    class="md:hidden border-b border-outline-gray-3 bg-surface-white dark:bg-surface-gray-1 px-4 py-3 flex flex-col gap-1 shadow-sm"
  >
    <a
      v-for="link in navLinks"
      :key="link.id"
      :href="link.url"
      class="px-3 py-2 rounded-md text-xs font-bold tracking-wider uppercase transition-colors"
      :class="
        activeTab === link.id
          ? 'bg-surface-gray-3 dark:bg-surface-gray-3 text-ink-gray-9 dark:text-ink-gray-1'
          : 'text-ink-gray-7 dark:text-ink-gray-8 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'
      "
      :aria-current="activeTab === link.id ? 'page' : undefined"
      @click="mobileMenuOpen = false"
    >
      {{ link.label }}
    </a>
  </div>
</template>
<script setup>
import { inject, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Avatar, Dropdown } from 'frappe-ui'
import { IconMenu2, IconX } from '@tabler/icons-vue'
import FossUnitedLogo from '@/components/FossUnitedLogo.vue'
import IndiaFossLogo from '@/components/IndiaFossLogo.vue'
import { fetchSessionProfile, sessionProfileResource } from '@/data/session'

const props = defineProps({
  // Pages with their own sticky toolbar (e.g. Schedule) opt out, so two sticky
  // layers do not compete for the same top edge.
  sticky: { type: Boolean, default: true },
  event: { type: Object, default: null },
  activeTab: { type: String, default: '' },
  showDevrooms: { type: Boolean, default: true },
  showBooths: { type: Boolean, default: true },
})

const route = useRoute()
const mobileMenuOpen = ref(false)

const isIndiaFoss = computed(() => {
  const fullPath = route?.fullPath || ''
  const paramRoute = (typeof route?.params?.route === 'string' ? route.params.route : '') || ''
  return (
    fullPath.includes('indiafoss') ||
    paramRoute.includes('indiafoss') ||
    Boolean(props.event?.event_name?.toLowerCase().includes('indiafoss')) ||
    Boolean(props.event?.route?.includes('indiafoss'))
  )
})

const currentYear = computed(() => {
  const path = `${route?.fullPath || ''} ${typeof route?.params?.route === 'string' ? route.params.route : ''} ${props.event?.route || ''}`
  const match = path.match(/indiafoss\/(\d{4})/)
  return match ? match[1] : '2026'
})

const activeTab = computed(() => {
  if (props.activeTab) return props.activeTab
  const path = route?.fullPath || ''
  if (path.includes('/schedule')) return 'schedule'
  if (path.includes('/cfp') || path.includes('/proposals')) return 'proposals'
  if (path.includes('/devrooms')) return 'devrooms'
  if (path.includes('/booths')) return 'booths'
  if (path.includes('/archive')) return 'archive'
  return ''
})

const navLinks = computed(() => {
  const links = [
    { id: 'overview', label: 'Overview', url: `/indiafoss/${currentYear.value}` },
    { id: 'schedule', label: 'Schedule', url: `/dashboard/schedule/indiafoss/${currentYear.value}` },
    { id: 'proposals', label: 'Proposals', url: `/dashboard/cfp/all/indiafoss/${currentYear.value}` },
  ]
  if (props.showDevrooms) {
    links.push({ id: 'devrooms', label: 'Devrooms', url: `/indiafoss/${currentYear.value}/devrooms` })
  }
  if (props.showBooths) {
    links.push({ id: 'booths', label: 'Booths', url: `/indiafoss/${currentYear.value}/booths` })
  }
  links.push({ id: 'archive', label: 'Archive', url: '/indiafoss/archive' })
  return links
})

const session = inject('$session')

const user_profile = sessionProfileResource

fetchSessionProfile()

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
