<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
  />
  <div v-if="chapter.data" class="flex flex-col md:flex-row">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:bg-surface-white focus:text-ink-gray-9 focus:px-3 focus:py-2 focus:rounded focus:shadow-lg"
    >
      Skip to main content
    </a>
    <SideNavbar title="Manage Chapter" :menu-items="sidebarMenuItems" />
    <main id="main-content" tabindex="-1" class="flex-1 min-w-0">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { usePageMeta, createResource, Dialog } from 'frappe-ui'
import { useRoute, useRouter, RouterView } from 'vue-router'
import SideNavbar from '@/components/NewAppSidebar.vue'

const route = useRoute()
const router = useRouter()
const session = inject('$session')
const dialogMessage = ref('')
const showDialog = ref(false)

onMounted(() => {
  isChapterMember.fetch()
})

const sidebarMenuItems = [
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Home',
        route: '/chapter',
      },
    ],
  },
  {
    items: [
      {
        icon: 'info',
        label: 'Details',
        route: `/chapter/${route.params.id}`,
      },
      {
        icon: 'calendar',
        label: 'Events',
        route: `/chapter/${route.params.id}/events`,
      },
      {
        icon: 'users',
        label: 'Members',
        route: `/chapter/${route.params.id}/members`,
      },
      {
        icon: 'mail',
        label: 'Chapter Mailing',
        route: `/chapter/${route.params.id}/mailing`,
      },
    ],
  },
]

const isChapterMember = createResource({
  url: 'fossunited.api.chapter.check_if_chapter_member',
  makeParams() {
    return {
      chapter: route.params.id,
      user: session.user,
    }
  },
  onSuccess(data) {
    if (data) {
      chapter.fetch()
      return
    }
    dialogMessage.value = 'You are not a member of this chapter'
    showDialog.value = true
    setTimeout(() => {
      router.push('/')
    }, 2000)
  },
  onError(error) {
    dialogMessage.value = error.messages
    showDialog.value = true
  },
})

const chapter = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      name: route.params.id,
      fields: ['*'],
    }
  },
})

usePageMeta(() => {
  return {
    title: 'Manage Chapter',
  }
})
</script>
