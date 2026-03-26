<template>
  <!-- Mobile: top bar -->
  <header
    class="flex md:hidden items-center gap-2 h-12 px-3 sticky top-0 z-40 bg-surface-menu-bar border-b border-outline-gray-1 w-full"
  >
    <button
      class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-surface-gray-2"
      @click="mobileOpen = true"
      aria-label="Open sidebar menu"
    >
      <div class="flex flex-col gap-4">
        <slot name="header"> </slot>
        <slot name="branding">
          <div class="mb-3 flex justify-between items-center">
            <div>
              <div class="font-fff text-ink-gray-9 uppercase">FOSS United</div>
              <div class="text-sm mt-2 tracking-wider text-ink-gray-6 uppercase">Dashboard</div>
            </div>
            <button
              class="p-1.5 rounded-md hover:bg-surface-gray-2 transition-colors"
              :title="currentTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
              @click="toggleTheme"
              :aria-label= "currentTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
            >
              <IconSunHighFilled v-if="currentTheme === 'dark'" :size="18" :stroke="1.5" />
              <IconMoonStars v-else :size="18" :stroke="1.5" />
            </button>
            <Button
              class="block md:hidden -mr-8 !rounded-full w-8 h-8"
              variant="outline"
              icon="arrow-left"
              @click="toggleSidebar = false"
              aria-label="Close sidebar"
            >
            </Button>
          </div>
        </slot>
        <slot name="pre-nav-items">
          <div v-if="title" class="text-lg font-semibold uppercase mt-2">{{ title }}</div>
        </slot>
        <slot name="nav-items">
          <div v-if="menuItems.length > 0" class="flex flex-col gap-2 my-2">
            <div v-for="(group, groupIndex) in menuItems" :key="groupIndex" class="my-1">
              <div
                v-if="group.parent_label"
                class="text-xs text-ink-gray-5 font-medium uppercase tracking-wide"
              >
                {{ group.parent_label }}
              </div>
              <div class="flex flex-col my-1 gap-1 text-ink-gray-6">
                <router-link
                  v-for="(item, index) in group.items"
                  :key="item.label"
                  :to="item.route"
                  class="w-full text-sm flex items-center gap-1 rounded-sm p-2 hover:bg-surface-gray-2 transition-colors"
                  :class="
                    isMenuItemActive(item.route, index)
                      ? 'font-medium text-ink-gray-9 bg-surface-gray-2'
                      : ''
                  "
                  @click="handleClick()"
                >
                  <FeatherIcon v-if="item.icon" class="w-4 h-4" :name="item.icon" />
                  <span>{{ item.label }}</span>
                </router-link>
              </div>
            </div>
          </div>
        </slot>
        <slot name="post-nav-items"></slot>
      </div>
      <div>
        <slot name="pre-user-actions">
          <p class="text-sm leading-normal tracking-tight font-medium text-ink-gray-5">
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
        </slot>
        <slot name="user-actions">
          <div class="hidden md:flex items-center justify-between text-ink-gray-8 py-2 my-1">
            <div class="flex items-center gap-2">
              <img
                v-if="user_profile.data?.profile_photo"
                :src="user_profile.data?.profile_photo"
                class="w-6 h-6 rounded-full"
              />
              <FeatherIcon v-else name="user" class="w-3 h-3" fill="black" />
              <span class="text-sm font-medium">{{ user_profile.data?.full_name }}</span>
            </div>
            <div>
              <Popover>
                <template #target="{ togglePopover }">
                  <Button icon="more-vertical" variant="ghost" @click="togglePopover()" />
                </template>
                <template #body-main>
                  <div class="flex flex-col gap-1 p-2">
                    <Button
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="My Profile"
                      :link="createAbsoluteUrlFromRoute('me')"
                      role="link"
                      aria-label="Go to my profile page"
                      variant="ghost"
                    />
                    <Button
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="Go To Website"
                      :link="createAbsoluteUrlFromRoute('')"
                      role="link"
                      aria-label="Go to home page"
                      variant="ghost"
                    />
                    <Button
                      variant="ghost"
                      theme="red"
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="Logout"
                      aria-label="Logout from website"
                      @click="session.logout.fetch()"
                    />
                  </div>
                </template>
              </Popover>
            </div>
          </div>
        </slot>
        <slot name="footer">
          <p class="text-ink-gray-6 text-xs leading-snug">
            FOSS United Foundation.
            <br />CC-BY-SA.
          </p>
        </slot>
      </div>
    </div>
  </div>

  <!-- For mobile screens -->
  <div class="md:hidden px-4 py-3 flex justify-between bg-surface-white">
    <div class="flex items-center gap-2">
      <Button icon="menu" class="text-ink-gray-9" variant="ghost" @click="toggleSidebar = true" aria-label="Open sidebar" />
    </div>
    <div class="flex items-center gap-2">
      <Popover>
        <template #target="{ togglePopover }">
        <button @click="togglePopover()" aria-label="Open user menu">
            <img
              v-if="user_profile.data?.profile_photo"
              :src="user_profile.data?.profile_photo"
              class="w-6 h-6 rounded-full"
            />
            <FeatherIcon v-else name="user" class="w-4 h-4" fill="black" />
          </button>
        </template>
        <template #body-main>
          <div class="flex flex-col gap-1 p-2">
            <Button
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="My Profile"
              :link="createAbsoluteUrlFromRoute('me')"
              variant="ghost"
            />
            <Button
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="Go To Website"
              :link="createAbsoluteUrlFromRoute('')"
              variant="ghost"
            />
            <Button
              variant="ghost"
              theme="red"
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="Logout"
              @click="session.logout.fetch()"
            />
          </div>
        </template>
      </Popover>
    </div>
  </div>

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
      :sections="allSections"
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
import { computed, inject, ref, h } from 'vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import {
  IconMenu,
  IconSun,
  IconMoon,
  IconExternalLink,
  IconLayoutSidebarLeftCollapse,
  IconLayoutSidebarLeftExpand,
} from '@tabler/icons-vue'
import { useRoute, useRouter } from 'vue-router'

const session = inject('$session')
const route = useRoute()
const router = useRouter()
const { currentTheme, toggleTheme } = useTheme()

const props = defineProps({
  menuItems: { type: Array, default: () => [] },
})

const STORAGE_KEY = 'foss_sidebar_collapsed'
const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')
const isHovering = ref(false)
const mobileOpen = ref(false)

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

const allSections = computed(() => [
  {
    items: [
      {
        label: currentTheme.value === 'dark' ? 'Switch to Light' : 'Switch to Dark',
        onClick: toggleTheme,
        icon: () => h(currentTheme.value === 'dark' ? IconSun : IconMoon, { class: 'w-4 h-4' }),
      },
      {
        label: isCollapsed.value ? 'Expand Sidebar' : 'Collapse Sidebar',
        onClick: () => { resolvedCollapsed.value = !isCollapsed.value },
        icon: () =>
          h(isCollapsed.value ? IconLayoutSidebarLeftExpand : IconLayoutSidebarLeftCollapse, {
            class: 'w-4 h-4',
          }),
      },
    ],
  },
  ...navSections.value,
])

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
      onClick: () => router.push(createAbsoluteUrlFromRoute('me')),
      icon: 'user',
    },
    {
      label: 'Go To Website',
      onClick: () => router.push(createAbsoluteUrlFromRoute('')),
      icon: 'external-link',
    },
    { label: 'Logout', onClick: () => session.logout.fetch(), icon: 'log-out' },
  ],
}))
</script>
