import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'Event',
    path: '/event/:id',
    component: () => import('@/pages/Event.vue'),
    children: [
      {
        path: '',
        name: 'EventDetails',
        component: () => import('@/pages/EventDetails.vue'),
      },
    ]
  },
  {
    name: 'Chapter',
    path: '/chapter/:id',
    component: () => import('@/pages/Chapter.vue'),
    children: [
      {
        path: '',
        name: 'ChapterDetails',
        component: () => import('@/pages/ChapterDetails.vue'),
      },
      {
        path: 'events',
        name: 'ChapterEvents',
        component: () => import('@/pages/ChapterEvents.vue'),
      },
      {
        path: 'members',
        name: 'ChapterMembers',
        component: () => import('@/pages/ChapterMembers.vue'),
      },
    ]
  }
]

let router = createRouter({
  history: createWebHistory('/dashboard'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
