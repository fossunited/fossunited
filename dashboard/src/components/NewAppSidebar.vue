<template>
  <!-- Mobile: top bar -->
  <header
    class="flex md:hidden items-center gap-2 h-12 px-3 sticky top-0 z-40 bg-surface-menu-bar border-b border-outline-gray-1 w-full"
  >
    <button
      class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-surface-gray-2"
      @click="mobileOpen = true"
    >
      <IconMenu class="w-4 h-4 text-ink-gray-6" />
    </button>
    <img :src="logo" class="w-6 h-6 rounded object-cover" alt="Logo" />
    <span class="text-base font-medium text-ink-gray-8">FOSS United</span>
  </header>

  <!-- Mobile: backdrop -->
  <div
    v-if="mobileOpen"
    class="fixed inset-0 bg-black/40 z-40 md:hidden"
    @click="mobileOpen = false"
  />

  <!-- Sidebar: sticky on desktop, fixed on mobile when open -->
  <div
    :class="
      mobileOpen
        ? 'fixed top-0 left-0 h-screen z-50'
        : 'h-screen hidden md:block md:sticky md:top-0'
    "
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <Sidebar
      v-model:collapsed="resolvedCollapsed"
      :class="mobileOpen ? '!w-60' : ''"
      :sections="navSections"
      :header="sidebarHeader"
    >
      <template #footer-items>
        <p
          v-if="!resolvedCollapsed"
          class="text-sm leading-normal tracking-tight font-medium text-ink-gray-5"
        >
          Need Help? Check out our
          <a
            class="underline flex gap-1 items-center"
            href="https://docs.fossunited.org/"
            target="_blank"
          >
            documentation
            <IconExternalLink class="w-4 h-4" />
          </a>
        </p>
        <p v-if="!resolvedCollapsed" class="text-ink-gray-6 text-xs leading-snug">
          FOSS United Foundation.<br />CC-BY-SA.
        </p>
      </template>
    </Sidebar>
  </div>
</template>

<script setup>
import { Sidebar, createResource, FeatherIcon, useTheme } from 'frappe-ui'
import { computed, inject, ref, h, watch } from 'vue'
import {
  IconMenu,
  IconSun,
  IconMoon,
  IconExternalLink,
} from '@tabler/icons-vue'
import { useRoute } from 'vue-router'

const session = inject('$session')
const route = useRoute()
const { currentTheme, toggleTheme } = useTheme()

const props = defineProps({
  menuItems: { type: Array, default: () => [] },
})

const STORAGE_KEY = 'foss_sidebar_collapsed'
const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')
const isHovering = ref(false)
const mobileOpen = ref(false)

watch(
  () => route.path,
  () => { mobileOpen.value = false },
)

let leaveTimer = null
const onMouseEnter = () => {
  clearTimeout(leaveTimer)
  isHovering.value = true
}
const onMouseLeave = () => {
  leaveTimer = setTimeout(() => {
    isHovering.value = false
  }, 200)
}

const resolvedCollapsed = computed({
  get: () => (mobileOpen.value ? false : isCollapsed.value && !isHovering.value),
  set: (val) => {
    if (!mobileOpen.value) {
      if (isHovering.value && isCollapsed.value) {
        // hover-expanded: button click means "stay expanded / pin open"
        isCollapsed.value = false
        isHovering.value = false
      } else {
        isCollapsed.value = val
        if (val) isHovering.value = false
      }
      localStorage.setItem(STORAGE_KEY, isCollapsed.value)
    }
  },
})

const user_profile = createResource({ url: 'fossunited.api.dashboard.get_session_user_profile' })
if (session.isLoggedIn && session.user !== 'Guest' && session.user !== 'Administrator') {
  user_profile.fetch()
}

const logo = computed(
  () =>
    user_profile.data?.profile_photo ??
    '/assets/fossunited/images/defaults/user_profile_image.png',
)

const isItemActive = (menuRoute, index) => {
  if (index === 0 && menuRoute !== route.path) return false
  return (
    menuRoute === route.path ||
    menuRoute === '/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/')
  )
}

const itemIcon = (icon, label) =>
  icon
    ? () => h(FeatherIcon, { name: icon, class: 'w-4 h-4' })
    : () =>
        h(
          'span',
          {
            class:
              'w-4 h-4 rounded text-[10px] font-semibold flex items-center justify-center bg-surface-gray-3 text-ink-gray-6 uppercase flex-shrink-0',
          },
          label?.[0] ?? '?',
        )

const navSections = computed(() =>
  props.menuItems.map((group) => ({
    label: group.parent_label || undefined,
    items: group.items.map((item, i) => ({
      label: item.label,
      to: item.route,
      isActive: isItemActive(item.route, i),
      icon: itemIcon(item.icon, item.label),
    })),
  })),
)


const sidebarHeader = computed(() => ({
  title: 'FOSS United',
  subtitle: user_profile.data?.full_name ?? '',
  logo: logo.value,
  menuItems: [
    {
      label: currentTheme.value === 'dark' ? 'Switch to Light' : 'Switch to Dark',
      onClick: toggleTheme,
      icon: 'sun',
    },
    {
      label: 'My Profile',
      onClick: () => (window.location.href = '/me'),
      icon: 'user',
    },
    {
      label: 'Go To Website',
      onClick: () => (window.location.href = '/'),
      icon: 'external-link',
    },
    { label: 'Logout', onClick: () => session.logout.fetch(), icon: 'log-out' },
  ],
}))
</script>
