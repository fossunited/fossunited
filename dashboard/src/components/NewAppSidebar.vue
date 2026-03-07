<template>
  <Sidebar :sections="computedSections" disable-collapse>
    <template #header>
      <slot name="branding">
        <div class="flex justify-between items-center px-2 pt-2 pb-1">
          <div>
            <div class="font-fff text-ink-gray-9 uppercase">FOSS United</div>
            <div class="text-sm mt-1 tracking-wider text-ink-gray-6 uppercase">Dashboard</div>
          </div>
          <button
            class="p-1.5 rounded-md hover:bg-surface-gray-2 transition-colors"
            :title="currentTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
            :aria-label="currentTheme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'"
            @click="toggleTheme"
          >
            <IconSunHighFilled v-if="currentTheme === 'dark'" :size="18" :stroke="1.5" />
            <IconMoonStars v-else :size="18" :stroke="1.5" />
          </button>
        </div>
      </slot>
      <slot name="pre-nav-items" />
      <div v-if="title" class="px-2 text-lg font-semibold uppercase mt-2">{{ title }}</div>
    </template>

    <template #footer-items>
      <slot name="post-nav-items"></slot>
      <slot name="pre-user-actions">
        <p class="text-sm leading-normal tracking-tight font-medium text-ink-gray-5 px-2 pb-1">
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
        <div class="flex items-center justify-between text-ink-gray-8 py-2 px-2">
          <div class="flex items-center gap-2">
            <img
              v-if="user_profile.data?.profile_photo"
              :src="user_profile.data?.profile_photo"
              class="w-6 h-6 rounded-full"
            />
            <FeatherIcon v-else name="user" class="w-3 h-3" fill="black" />
            <span class="text-sm font-medium">{{ user_profile.data?.full_name }}</span>
          </div>
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
      </slot>
      <slot name="footer">
        <p class="text-ink-gray-6 text-xs leading-snug px-2 pb-2">
          FOSS United Foundation.
          <br />CC-BY-SA.
        </p>
      </slot>
    </template>
  </Sidebar>
</template>

<script setup>
import { Sidebar, createResource, FeatherIcon, Popover, useTheme } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { computed, inject } from 'vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { IconExternalLink, IconSunHighFilled, IconMoonStars } from '@tabler/icons-vue'

const route = useRoute()
const session = inject('$session')
const { currentTheme, toggleTheme } = useTheme()

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  menuItems: {
    type: Array,
    default: () => [],
  },
})

const user_profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

if (session.isLoggedIn && session.user != 'Guest' && session.user != 'Administrator') {
  user_profile.fetch()
}

const isMenuItemActive = (menuRoute, index) => {
  if (index === 0 && menuRoute !== route.path) {
    return false
  }
  return (
    menuRoute === route.path ||
    menuRoute === '/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/')
  )
}

const computedSections = computed(() =>
  props.menuItems.map((group) => ({
    label: group.parent_label,
    items: group.items.map((item, index) => ({
      label: item.label,
      icon: item.icon,
      to: item.route,
      isActive: isMenuItemActive(item.route, index),
    })),
  })),
)
</script>
