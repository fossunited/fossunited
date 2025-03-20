<template>
  <div class="flex flex-col gap-4 bg-white w-full p-8 border rounded items-center">
    <IconFileSad size="40" stroke="1.6" />
    <div class="prose-sm text-center">
      <h3>Proposal form is closed!</h3>
      <p v-if="isPastDeadline()">The deadline for submitting your proposal has passed.</p>
      <p>
        If you have any questions, please contact us at
        <a :href="`mailto:${organizerEmail.data?.email}`">{{ organizerEmail.data?.email }}</a>
      </p>
    </div>
  </div>
</template>
<script setup>
import { IconFileSad } from '@tabler/icons-vue'
import { createResource } from 'frappe-ui'
import { computed, inject } from 'vue'

const cfpData = inject('$cfpData')

const organizerEmail = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      fieldname: 'email',
      filters: {
        name: cfpData.data.chapter,
      },
    }
  },
  auto: true,
})

const isPastDeadline = () => {
  const deadline = cfpData.data?.deadline
  if (deadline == null) return false
  const now = new Date()
  const deadlineDate = new Date(deadline)
  return now > deadlineDate
}
</script>
