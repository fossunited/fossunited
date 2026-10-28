<template>
  <div class="flex h-svh flex-col items-center justify-center">
    <component
      :is="getIcon()"
      class="m-2 h-12 w-12 rounded-full bg-surface-gray-3 p-2 text-ink-gray-8"
    ></component>
    <h1 class="text-3xl-bold">{{ getTitle() }}</h1>
    <p class="mb-2">{{ getMessage() }}</p>
    <Button label="Go Home" route="/" />
  </div>
</template>
<script setup>
import { IconError404, IconLockAccess } from '@tabler/icons-vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const getIcon = () => {
  switch (route.query.error) {
    case 'not-authorized':
      return IconLockAccess
    default:
      return IconError404
  }
}

const getMessage = () => {
  switch (route.query.error) {
    case 'not-authorized':
      return 'You are not authorized to view this page'
    default:
      return 'The page you are looking for does not exist!'
  }
}

const getTitle = () => {
  switch (route.query.error) {
    case 'not-authorized':
      return 'Not authorized!'
    default:
      return 'Page not found'
  }
}
</script>
