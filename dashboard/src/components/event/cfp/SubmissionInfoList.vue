<script setup>
import SubmissionInfoListItem from './SubmissionInfoListItem.vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import SubmissionStatusToggler from './SubmissionStatusToggler.vue'
import { inject } from 'vue'

dayjs.extend(relativeTime)

const submission = inject('curr_submission')
</script>
<template>
  <div class="flex flex-col">
    <SubmissionInfoListItem
      label="Submitted On"
      :value="dayjs(submission.data.creation).format('D MMM YYYY, h:mm A ')"
    ></SubmissionInfoListItem>
    <SubmissionInfoListItem
      label="Last Modified"
      :value="dayjs(submission.data.modified).format('D MMM YYYY, h:mm A ')"
    ></SubmissionInfoListItem>
    <SubmissionInfoListItem label="Status">
      <SubmissionStatusToggler></SubmissionStatusToggler>
    </SubmissionInfoListItem>
  </div>
</template>
