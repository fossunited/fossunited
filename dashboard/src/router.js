import { createRouter, createWebHistory } from 'vue-router'
import { userResource } from '@/data/user'
import { sessionUser } from './data/session'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/buy-tickets',
    name: 'checkout',
    component: () => import('@/pages/BuyTickets.vue'),
    meta: { isPublicPage: true },
  },
  {
    path: '/payment-success',
    name: 'success',
    component: () => import('@/pages/PaymentSuccess.vue'),
    meta: { isPublicPage: true },
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
      {
        path: 'rsvp',
        name: 'EventRsvp',
        component: () => import('@/pages/EventRsvp.vue'),
        children: [
          {
            path: '',
            name: 'EventRsvpManage',
            component: () => import('@/pages/EventRsvpManage.vue'),
          },
          {
            path: 'create',
            name: 'EventRsvpCreate',
            component: () => import('@/pages/EventRsvpCreate.vue'),
          },
          {
            path: 'edit',
            name: 'EventRsvpEdit',
            component: () => import('@/pages/EventRsvpEdit.vue'),
          },
          {
            path: 'insights',
            name: 'EventRsvpInsights',
            component: () => import('@/pages/EventRsvpInsights.vue'),
          },
        ],
      },
      {
        path: 'cfp',
        name: 'EventCfp',
        component: () => import('@/pages/EventCfp.vue'),
        children: [
          {
            path: '',
            name: 'EventCfpManage',
            component: () => import('@/pages/EventCfpManage.vue'),
          },
          {
            path: 'create',
            name: 'EventCfpCreate',
            component: () => import('@/pages/EventCfpCreate.vue'),
          },
          {
            path: 'edit',
            name: 'EventCfpEdit',
            component: () => import('@/pages/EventCfpEdit.vue'),
          },
          {
            path: 'insights',
            name: 'EventCfpInsights',
            component: () => import('@/pages/EventCfpInsights.vue'),
          },
        ],
      },
      {
        path: 'volunteers',
        name: 'EventVolunteers',
        component: () => import('@/pages/EventVolunteers.vue'),
      },
    ],
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
        path: 'events/create',
        name: 'ChapterEventsCreate',
        component: () => import('@/pages/CreateEventForm.vue'),
      },
      {
        path: 'members',
        name: 'ChapterMembers',
        component: () => import('@/pages/ChapterMembers.vue'),
      },
    ],
  },
  {
    path: '/register-for-hackathon',
    name: 'HackathonRegister',
    component: () => import('@/pages/hackathon/Register.vue'),
  },
  {
    path: '/my-hackathons',
    name: 'MyHackathons',
    component: () => import('@/pages/hackathon/MyHackathons.vue'),
  },
  {
    path: '/hack/:permalink',
    children:[
      {
        path: '',
        name: 'InitialRegister',
        component: () => import('@/pages/hackathon/InitRegister.vue')
      },
      {
        path: 'create-team',
        name: 'CreateHackathonTeam',
        component: () => import('@/pages/hackathon/CreateTeam.vue'),
      },
      {
        path: 'create-project',
        name: 'CreateHackathonProject',
        component: () => import('@/pages/hackathon/CreateProject.vue'),
      },
      {
        path: 'my-team',
        name: 'MyHackathonTeam',
        component: () => import('@/pages/hackathon/MyTeam.vue'),
      },
      {
        path: 'project',
        name: 'MyHackathonProject',
        component: () => import('@/pages/hackathon/MyProject.vue'),
      }
    ]
  },
]

let router = createRouter({
  history: createWebHistory('/dashboard'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = Boolean(sessionUser())
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn && !to.meta.isPublicPage) {
    window.location.href = `/login?redirect-to=/dashboard${to.path}`
  } else {
    next()
  }
})

export default router
