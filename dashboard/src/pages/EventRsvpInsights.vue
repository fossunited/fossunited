<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 mt-5">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">
          Attendees

          <span class="text-gray-700 text-base font-normal"
            >({{ submissions.data.length }}/{{ rsvp_form.data.max_rsvp_count }})</span
          >
        </div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList">Download</Button>
      </div>
      <ListView
        :columns="[
          { label: 'Name', key: 'name1' },
          { label: 'Email', key: 'email' },
          { label: 'I am a', key: 'im_a' },
          { label: 'Designation', key: 'designation' },
          { label: 'Company', key: 'company' },
        ]"
        :rows="submissions.data"
        row-key="name"
        :options="{
          selectable: false,
          emptyState: {
            description: 'No one has RSVPed for the event yet.',
          },
        }"
      />
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createListResource, createResource, ListView, Button } from 'frappe-ui'

const route = useRoute()

const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    fields: ['*'],
    filters: {
      event: route.params.id,
    },
  },
  auto: true,
})

function censorEmail(email) {
    const [name, domain] = email.split('@');

    if (name.length <= 7) {
        // For short usernames, keep first and last characters only
        return name[0] + '*'.repeat(name.length - 2) + name.slice(-1) + '@' + domain;
    }

    const first3 = name.slice(0, 3);
    const middleChar = name[Math.floor(name.length/2)]
    const last3 = name.slice(-3);

    const starCount = (name.length - 7); // total characters to replace with asterisks
    let starCount1 = 0
    let starCount2 = 0
    if ((starCount/2) == (Math.floor(starCount/2))) {
      starCount1 = starCount/2
      starCount2 = starCount/2
    } else {
      // Add another asterisk to balance it out
      starCount1 = starCount/2+1
      starCount2 = starCount/2
    }
    const censored = first3 + '*'.repeat(starCount1) + middleChar + '*'.repeat(starCount2) + last3;

    return censored + '@' + domain;
}

const submissions = createListResource({
  doctype: 'FOSS Event RSVP Submission',
  fields: ['*'],
  filters: {
    event: route.params.id,
  },
  pageLength: 99999,
  auto: true,
  transform(data) {
    data.forEach((submission) => {
      submission.email = censorEmail(submission.email)
    })
  },
})

const downloadAttendeeList = () => {
  let csv = 'name,email,status,designation,company\n'
  csv = csv+submissions.data
    .map((submission) => {
      return [submission.name1, submission.email, submission.im_a, submission.designation, submission.company].join(',')
    })
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Attendee List-${rsvp_form.data.event_name}-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
