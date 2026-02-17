<template>
  <div class="h-svh flex flex-col items-center justify-center">
    <component
      :is="getIcon()"
      class="m-2 w-12 h-12 bg-surface-gray-3 text-ink-gray-8 p-2 rounded-full"
    ></component>
    <h1 class="text-2xl font-bold">{{ getTitle() }}</h1>
    <p class="mb-2">{{ getMessage() }}</p>
    <Button label="Go Home" link="/" />
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
