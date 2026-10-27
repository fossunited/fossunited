<template>
  <!-- Mobile: top bar -->
  <header
    class="flex md:hidden items-center gap-2 h-12 px-3 sticky top-0 z-40 bg-surface-base border-b border-outline-gray-1 w-full"
  >
    <button
      type="button"
      aria-label="Open navigation menu"
      class="w-8 h-8 flex items-center justify-center rounded-5 hover:bg-surface-gray-2"
      @click="mobileOpen = true"
    >
      <IconMenu class="w-4 h-4 text-ink-gray-6" aria-hidden="true" />
    </button>
    <img :src="logo" class="w-6 h-6 rounded-4 object-cover" alt="Logo" />
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
    <!--
      frappe-ui 1.0's Sidebar is a bare <nav> frame: the old `:header`,
      `:sections` and `#footer-items` API is gone (silently ignored), so the
      header, groups, footer and collapse toggle are composed here instead.
      The old frame's border and padding are re-added by hand.
    -->
    <Sidebar
      v-model:collapsed="resolvedCollapsed"
      class="border-r border-outline-gray-1"
      :class="mobileOpen ? '!w-60' : ''"
    >
      <SidebarHeader
        :title="sidebarHeader.title"
        :subtitle="sidebarHeader.subtitle"
        :logo="sidebarHeader.logo"
        :menu-items="sidebarHeader.menuItems"
      />
      <div class="flex flex-1 flex-col overflow-y-auto overflow-x-hidden px-2 pb-2">
        <SidebarSection
          v-for="(section, sectionIndex) in navSections"
          :key="section.label ?? `section-${sectionIndex}`"
          :label="section.label"
        >
          <SidebarItem
            v-for="item in section.items"
            :key="`${item.label}-${item.route}`"
            :label="item.label"
            :route="item.route"
            :active="item.isActive"
            :icon="item.icon"
          />
        </SidebarSection>

        <div class="mt-auto flex flex-col gap-2 pt-2">
          <p
            v-if="!resolvedCollapsed"
            class="text-sm leading-normal tracking-tight font-medium text-ink-gray-7 dark:text-ink-gray-8"
          >
            Need Help? Check out our
            <a
              class="underline flex gap-1 items-center"
              href="https://docs.fossunited.org/"
              target="_blank"
            >
              documentation
              <IconExternalLink class="w-4 h-4" aria-hidden="true" />
            </a>
          </p>
          <p
            v-if="!resolvedCollapsed"
            class="text-ink-gray-7 dark:text-ink-gray-8 text-xs leading-snug"
          >
            FOSS United Foundation.<br />CC-BY-SA.
          </p>
          <SidebarCollapseToggle />
        </div>
      </div>
    </Sidebar>
  </div>
</template>

<script setup>
import {
  Sidebar,
  SidebarCollapseToggle,
  SidebarHeader,
  SidebarItem,
  SidebarSection,
  useColorScheme,
} from 'frappe-ui'
import { computed, inject, ref, h, watch } from 'vue'
import { fetchSessionProfile, sessionProfileResource } from '@/data/session'
import {
  IconMenu,
  IconSun,
  IconMoon,
  IconExternalLink,
  IconUser,
  IconLogout,
  IconArrowLeft,
  IconInfoCircle,
  IconCircleCheck,
  IconMicrophone,
  IconClock,
  IconBriefcase,
  IconDeviceDesktop,
  IconHeart,
  IconMail,
  IconTag,
  IconUserCheck,
  IconBolt,
  IconEdit,
  IconUsers,
  IconCalendar,
  IconMapPin,
  IconGavel,
  IconFileText,
  IconTicket,
} from '@tabler/icons-vue'
import { useRoute } from 'vue-router'

// Shared sidebar/profile-menu icon vocabulary: items authored in this file,
// in page-level `sidebarMenuItems` arrays, and returned by the
// `fossunited.api.sidebar.get_sidebar_items` backend all use these names.
const ICON_MAP = {
  'arrow-left': IconArrowLeft,
  info: IconInfoCircle,
  'check-circle': IconCircleCheck,
  mic: IconMicrophone,
  clock: IconClock,
  briefcase: IconBriefcase,
  monitor: IconDeviceDesktop,
  heart: IconHeart,
  mail: IconMail,
  tag: IconTag,
  'user-check': IconUserCheck,
  zap: IconBolt,
  edit: IconEdit,
  users: IconUsers,
  calendar: IconCalendar,
  user: IconUser,
  'map-pin': IconMapPin,
  'gavel': IconGavel,
  'file-text': IconFileText,
  ticket: IconTicket,
}

const session = inject('$session')
const route = useRoute()
const { colorScheme, toggleColorScheme } = useColorScheme()

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

const user_profile = sessionProfileResource
fetchSessionProfile()

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
  icon && ICON_MAP[icon]
    ? () => h(ICON_MAP[icon], { class: 'w-4 h-4' })
    : () =>
        h(
          'span',
          {
            class:
              'w-4 h-4 rounded-4 text-[10px] font-semibold flex items-center justify-center bg-surface-gray-3 text-ink-gray-6 uppercase flex-shrink-0',
          },
          label?.[0] ?? '?',
        )

const navSections = computed(() =>
  props.menuItems.map((group) => ({
    label: group.parent_label || undefined,
    items: group.items.map((item, i) => ({
      label: item.label,
      route: item.route,
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
      label: colorScheme.value === 'dark' ? 'Switch to Light' : 'Switch to Dark',
      onClick: toggleColorScheme,
      icon: colorScheme.value === 'dark' ? IconSun : IconMoon,
    },
    {
      label: 'My Profile',
      onClick: () => (window.location.href = '/me'),
      icon: IconUser,
    },
    {
      label: 'Go To Website',
      onClick: () => (window.location.href = '/'),
      icon: IconExternalLink,
    },
    { label: 'Logout', onClick: () => session.logout.fetch(), icon: IconLogout },
  ],
}))
</script>
