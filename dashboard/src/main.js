import './index.css'

import { createApp, h } from 'vue'
import router from './router'
import App from './App.vue'
import { session } from './data/session'
import dayjs from 'dayjs'
import { showError } from '@/helpers/utils'

import {
  Button,
  Card as FrappeCard,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
  useTheme,
} from 'frappe-ui'

if (!localStorage.getItem('theme')) {
  localStorage.setItem('theme', 'light')
}
document.documentElement.setAttribute('data-theme', localStorage.getItem('theme'))

const { initializeTheme } = useTheme()
initializeTheme()

window.showError = showError
const app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.provide('$session', session)
app.provide('$dayjs', dayjs)

app.component('Button', Button)
app.component('Input', Input)

app.component('Card', {
  name: 'AppCard',
  inheritAttrs: false,
  setup(props, { attrs, slots }) {
    return () =>
      h(
        FrappeCard,
        {
          ...attrs,
          class: ['frappeui-card', attrs.class],
        },
        slots,
      )
  },
})

app.mount('#app')
