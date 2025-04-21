<template>
  <div class="flex flex-col gap-2 justify-between mb-4">
    <!-- Search -->
    <FormControl
      v-model="filters.talk_title"
      class="w-full"
      variant="outline"
      label="Search"
      type="search"
    />

    <div class="flex justify-between gap-2">
      <FormControl
        v-model="filters.only_show_unreviewed"
        variant="outline"
        label="Show Unreviewed By Me"
        type="checkbox"
        size="sm"
      />

      <!-- Filter Dropdown -->
      <Popover>
        <template #target="{ togglePopover }">
          <Button label="Filters" variant="outline" @click="togglePopover()">
            <template #prefix>
              <Badge v-if="getFilterCount()" :label="getFilterCount()" variant="solid" size="sm" />
              <IconFilter v-else class="w-4 h-4" />
            </template>
            <template #suffix>
              <Button
                v-if="getFilterCount()"
                variant="ghost"
                icon="x"
                size="sm"
                class="-ml-2"
                @click="clearFilters"
              />
            </template>
          </Button>
        </template>
        <template #body-main>
          <div class="flex flex-col gap-2 p-2 w-[200px]">
            <FormControl
              v-model="filters.status"
              label="Status"
              type="select"
              :options="[
                { label: '', value: '' },
                { label: 'Accepted', value: 'Accepted' },
                { label: 'Not Yet Decided', value: 'Not Yet Decided' },
                { label: 'Declined', value: 'Declined' },
              ]"
              variant="outline"
            />
            <FormControl
              v-model="filters.session_type"
              label="Session Type"
              type="select"
              :options="[
                { label: '', value: '' },
                { label: 'Talk', value: 'Talk' },
                { label: 'Lightning Talk', value: 'Lightning Talk' },
                { label: 'Panel Discussion', value: 'Panel Discussion' },
                { label: 'Workshop', value: 'Workshop' },
                { label: 'Birds of Feather(BoF)', value: 'Birds of Feather(BoF)' },
              ]"
              variant="outline"
            />
            <FormControl
              v-model="filters.intended_audience"
              label="Intended Audience"
              type="select"
              :options="[
                { label: '', value: '' },
                { label: 'Beginners', value: 'Beginner' },
                { label: 'Intermediate', value: 'Intermediate' },
                { label: 'Advanced', value: 'Advanced' },
              ]"
              variant="outline"
            />
          </div>
        </template>
      </Popover>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, watch } from 'vue'
import { FormControl, Popover, Badge } from 'frappe-ui'
import { IconFilter } from '@tabler/icons-vue'

const emit = defineEmits(['search'])

const filters = reactive({
  talk_title: '',
  only_show_unreviewed: 0,
  status: '',
  session_type: '',
  intended_audience: '',
})

const clearFilters = () => {
  filters.status = ''
  filters.session_type = ''
  filters.intended_audience = ''
}

const getFilterCount = () => {
  let count = 0
  Object.keys(filters).forEach((key) => {
    if (key !== 'talk_title' && key !== 'only_show_unreviewed' && filters[key]) {
      count++
    }
  })
  return count
}

watch(
  () => filters,
  () => {
    emit('search', filters)
  },
  { deep: true },
)
</script>
