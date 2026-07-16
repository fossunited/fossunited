<script setup>
import InsightCard from '@/components/ui/InsightCard.vue'
import { IconArrowUp } from '@tabler/icons-vue'
import { createResource, Badge, Tooltip } from 'frappe-ui'
import { statusIndicatorColor } from '@/helpers/cfp'

const props = defineProps({
  eventId: {
    type: String,
    required: true,
  },
  currentFilter: {
    type: String,
    default: '',
  },
})

const insights = createResource({
  url: 'fossunited.api.cfp.get_cfp_submissions_insight',
  makeParams() {
    return {
      event_id: props.eventId,
    }
  },
  auto: true,
})

const emit = defineEmits(['select-insight'])

function handleClick(label) {
  const filterValue = label === 'Total' ? '' : label
  emit('select-insight', filterValue)
}

function filterValueFor(label) {
  return label === 'Total' ? '' : label
}

function tooltipText(label) {
  return label === 'Total' ? 'Show all proposals' : `Filter by: ${label}`
}

const getClasses = {
  'Total Submissions': 'md:col-span-2 lg:col-span-1',
}
</script>

<template>
  <div class="flex flex-col gap-4 my-2 w-full">
    <h4 class="text-xl font-medium">Insights</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <Tooltip
        v-for="insight in insights.data"
        :key="insight.name"
        :class="getClasses[insight.label]"
        :text="tooltipText(insight.label)"
        placement="top"
      >
        <InsightCard
          class="h-full"
          :title="insight.label"
          :value="insight.count"
          :is-active="filterValueFor(insight.label) === currentFilter"
          @click="() => handleClick(insight.label)"
        >
          <template v-if="insight.today" #post-value>
            <Badge class="w-fit" theme="green">
              <IconArrowUp class="w-3 h-3" />
              <span> {{ insight.today }} </span>
            </Badge>
          </template>
          <template #description>
            <div
              class="w-full h-1 rounded-full bg-opacity-50"
              :class="'bg-' + statusIndicatorColor(insight.label)"
            ></div>
          </template>
        </InsightCard>
      </Tooltip>
    </div>
  </div>
</template>
