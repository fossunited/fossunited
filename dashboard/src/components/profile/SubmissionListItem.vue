<template>
  <div
    class="p-4 border-b first:border-t border-outline-gray-4 w-full flex flex-col gap-3 focus:bg-surface-gray-1 focus:outline-none focus:ring-2 focus:ring-gray-700 hover:cursor-pointer hover:bg-surface-gray-1"
    tabindex="0"
    @click="navigateToProposal"
    @keydown.enter="navigateToProposal"
    @keydown.space.prevent="navigateToProposal"
    role="link"
    :aria-labelledby="`proposal-title-${proposal.name}`"
  >
    <h4 :id="`proposal-title-${proposal.name}`" class="text-base font-medium">
      {{ proposal.talk_title }}
    </h4>
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
      <div class="flex flex-wrap gap-2 items-center divide-x-2 text-ink-gray-8">
        <Badge class="!rounded-sm" :theme="getTheme[proposal.status]">{{ proposal.status }}</Badge>
        <span class="text-sm uppercase pl-2">{{ proposal.event_name }}</span>
        <span class="text-sm uppercase pl-2">{{ proposal.chapter }}</span>
      </div>
      <span class="text-xs text-ink-gray-5">{{ getFormattedModified(proposal.modified) }}</span>
    </div>
  </div>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useRouter } from 'vue-router'
dayjs.extend(relativeTime)

const router = useRouter()

const props = defineProps({
  proposal: {
    type: Object,
    required: true,
  },
})

const navigateToProposal = () => {
  router.push({ name: 'Proposal Edit', params: { id: props.proposal.name } })
}

const getTheme = {
  'Review Pending': 'orange',
  Approved: 'green',
  Rejected: 'red',
  Withdrawn: 'red',
  Screening: 'blue',
}

const getFormattedModified = (date) => {
  let fromNow = dayjs(date).fromNow()

  // Extract the number and first letter of the time unit
  const match = fromNow.match(/(\d+)\s*(\w)/)

  if (match) {
    const [, number, unit] = match
    return `${number}${unit.charAt(0)}`
  }

  return 'now'
}
</script>
