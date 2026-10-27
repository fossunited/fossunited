<template>
  <div class="m-3 flex flex-row items-center justify-center">
    <Card title="Login to your FrappeUI App!" class="w-full max-w-md mt-4">
      <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
        <FormControl
          v-model="email"
          required
          name="email"
          type="text"
          placeholder="johndoe@email.com"
          label="User ID"
        />
        <FormControl
          v-model="password"
          required
          name="password"
          type="password"
          placeholder="••••••"
          label="Password"
        />
        <Button type="submit" :loading="session.login.loading" variant="solid">Login</Button>
      </form>
    </Card>
  </div>
</template>

<script setup>
import { inject, ref } from 'vue'
import { FormControl } from 'frappe-ui'
import Card from '@/components/ui/Card.vue'

let session = inject('$session')
const email = ref('')
const password = ref('')

function submit() {
  session.login.submit({
    email: email.value,
    password: password.value,
  })
}
</script>
