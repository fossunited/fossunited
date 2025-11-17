<script setup>
import LivePing from '../animation/LivePing.vue'
import { Badge, Button } from 'frappe-ui'
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  cfp: {
    type: Object,
    required: true,
  },
})

const getBadgeTheme = computed(() => {
  if (props.cfp.status == 'Live') {
    return 'green'
  }
  if (props.cfp.status == 'Closed') {
    return 'red'
  }
  return 'gray'
})
</script>
<template>
  <div
    class="p-6 flex justify-between items-center gap-4 bg-white rounded w-full border border-gray-300"
  >
    <div class="flex flex-col gap-2">
      <div class="flex gap-2 items-center">
        <h4 class="text-lg font-medium">Call For Proposals</h4>
        <Badge size="lg" class="!rounded" :theme="getBadgeTheme" :label="cfp.status">
          <template v-if="cfp.status == 'Live'" #prefix>
            <LivePing />
          </template>
        </Badge>
      </div>
      <p class="text-sm text-gray-600">Propose your ideas here and we will get back to you.</p>
      <div v-if="cfp.deadline" class="text-sm mt-2">
        <span class="text-gray-600">Deadline: </span>
        <span class="text-gray-800">{{ dayjs(cfp.deadline).format('DD MMM YYYY') }}</span>
      </div>
    </div>
    <router-link
      v-if="cfp.status == 'Live'"
      :to="'/cfp/apply/' + $route.params.route"
      variant="solid"
      class="py-3 px-5 bg-gray-900 hover:bg-gray-800 transition-colors duration-200 text-white rounded text-center uppercase text-sm font-semibold tracking-wider"
    >
      Submit a Proposal
    </router-link>
  </div>
</template>
