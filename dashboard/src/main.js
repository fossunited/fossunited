import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { session } from './data/session'
import dayjs from 'dayjs'
import { showError } from '@/helpers/utils'

import {
  Button,
  setConfig,
  frappeRequest,
  resourcesPlugin,
  useColorScheme,
} from 'frappe-ui'

useColorScheme()

window.showError = showError
const app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.provide('$session', session)
app.provide('$dayjs', dayjs)

app.component('Button', Button)

app.mount('#app')
